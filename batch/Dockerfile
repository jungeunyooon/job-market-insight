FROM python:3.12-slim

WORKDIR /app

COPY batch/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY batch /app/batch
COPY data /app/data

WORKDIR /app/batch

ENTRYPOINT ["python", "main.py"]
