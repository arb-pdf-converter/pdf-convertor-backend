FROM python:3.11

WORKDIR /app

# Install system deps for Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:$PORT"]
