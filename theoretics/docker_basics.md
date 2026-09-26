# Docker - fundamente

Note tehnice pe fundamentele Docker. Cifrele sunt masurate, nu citate.

## Imagine si container

O imagine este un pachet read-only pe disc: cod, runtime, librarii, o bucata de OS si metadate despre pornire. Nu ruleaza singura. Containerul este o instanta pornita din imagine, cu un strat read-write propriu deasupra.

Dintr-o imagine pot porni oricate containere simultan. Ele impart layerele read-only (deci nu se dubleaza pe disc), dar fiecare are stratul lui de scriere, procesul lui, IP-ul si hostname-ul lui. Test: un fisier scris intr-un container nu e vizibil din altul pornit din aceeasi imagine.

## Layere

Un layer este efectul pe disc al unei instructiuni de build (un diff de filesystem), nu instructiunea in sine. In `docker history python:3.12`, instructiunile care nu ating fisiere (`ENV`, `CMD`) apar cu 0B, iar un `RUN apt install` adauga sute de MB. O baza `python:3.12` mosteneste ~1.2GB inainte de orice cod propriu.

Layerele se citesc de jos in sus (OS de baza -> comanda finala) si se refolosesc intre imagini care pornesc din aceeasi baza.

## `docker run` pas cu pas

1. Verifica imaginea local; daca lipseste, o descarca.
2. Creeaza containerul, adaugand stratul read-write peste layerele imaginii.
3. Il izoleaza prin namespace-uri de kernel (spatiu de procese si retea proprii).
4. Porneste procesul din `CMD`/`ENTRYPOINT`, care devine PID 1.

Izolarea nu e o functie Docker, ci a kernel-ului Linux; Docker doar o orchestreaza.

## Containere efemere si volume

`docker rm` sterge containerul impreuna cu stratul read-write, deci datele scrise la runtime se pierd; imaginea ramane neatinsa. Un container e efemer prin design. Datele care trebuie sa persiste (ex. o baza de date) stau in volume, in afara containerului. De aceea `compose down` pastreaza volumele, iar `down -v` le sterge.

## Build context si `.dockerignore`

La `docker build .`, punctul defineste build context-ul: fisierele trimise catre daemon inainte de build. Comportamentul, masurat pe un folder cu un fisier inutil de 500MB:

| Build | context transferat |
|-------|-------------------|
| doar `FROM alpine` | 2B |
| cu `COPY . .` | 524MB |
| `COPY . .` + `.dockerignore` | 4.04kB |

Problema nu e folderul mare, ci `COPY . .` peste continut inutil. Un `.dockerignore` corect reduce si timpul de build, si dimensiunea imaginii.

## Imagini dangling

Un build fara `-t` produce o imagine fara nume, invizibila la `docker images` obisnuit (vizibila cu `docker images -f dangling=true`). Asa se umple discul in timp. Curatare cu `docker image prune`. Regula: mereu `docker build -t nume:tag .`.

## Mediu de lucru (WSL2)

Proiectul sta pe `/mnt/c/` (disc Windows montat in WSL). I/O-ul acolo e mai lent decat pe filesystem-ul nativ (`~/`), relevant la build-uri. Ales constient deocamdata; primul suspect daca build-urile devin lente.

## Imagine naiva vs optimizata

Aceeasi aplicatie FastAPI, doua Dockerfile-uri:

| Metrica | naiva | optimizata |
|---------|-------|-----------|
| Dimensiune | 1.69GB | 270MB |
| Rebuild dupa modificare cod | ~10s, pip se reinstaleaza | ~1.7s, pip cached |
| User | root | non-root dedicat |
| Build context | tot folderul | 64B, cu `.dockerignore` |

**Base image.** Trecerea la `python:3.12-slim` taie ~84% din dimensiune. `slim` nu are unelte de build, deci o dependenta care se compileaza din surse poate crapa; pentru wheels precompilate merge.

**Ordinea = cache.** Copierea codului inainte de `pip install` invalideaza layerul de instalare la orice modificare de cod. Corect: `COPY requirements.txt` -> `pip install` -> `COPY . .`. Ce se schimba rar sta mai sus. Rezultat: rebuild de la ~10s la sub 2s.

**Non-root.** User creat si comutat cu `USER`, plasat dupa `pip install` (pip scrie in locatii de sistem si are nevoie de root; comutarea prea devreme da permission denied).

**Doua capcane.** `0.0.0.0` = serverul asculta pe toate interfetele (obligatoriu in container); `localhost` = adresa la care se conecteaza clientul. Si: o comanda ruleaza in container doar dupa `docker run`/`docker exec` - altfel ruleaza pe host.