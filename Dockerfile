FROM python:3.11

WORKDIR /app

# System deps for Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render injects $PORT automatically
CMD gunicorn --bind 0.0.0.0:$PORT main:app
