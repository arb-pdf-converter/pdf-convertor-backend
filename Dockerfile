FROM python:3.11-slim

WORKDIR /app

# Minimal deps for Flask + PDF
RUN apt-get update && apt-get install -y \
    gcc libjpeg-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "main:app"]
