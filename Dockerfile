FROM python:3.11-slim

# Fix Render build issues
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $$PORT --workers 1"]
