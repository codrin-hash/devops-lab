FROM python:3.12

WORKDIR /app

COPY ../purposefully_naive_dockerfile .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]