FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Volumes tipicos para trocar dados de entrada/saida sem rebuildar a imagem:
#   docker run -v $(pwd)/data:/app/data etl-qualidade
VOLUME ["/app/data", "/app/logs"]

ENTRYPOINT ["python", "main.py"]
