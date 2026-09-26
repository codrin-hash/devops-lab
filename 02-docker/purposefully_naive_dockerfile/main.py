from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "DevOps lab by Codrin"}


@app.get("/health")
def health():
    return {"status": "ok"}