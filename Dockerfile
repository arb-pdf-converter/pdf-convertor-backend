FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y \
        gcc \
        ghostscript \
        libjpeg-dev \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"]
