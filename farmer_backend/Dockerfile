FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
      curl \
      postgresql-client \
      libpq-dev \
      build-essential \
      libgl1-mesa-glx \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to /app to match the volume mount in docker-compose.yml
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code (optional if you're using a volume mount)
COPY . .

# Expose the port your FastAPI app listens on
EXPOSE 8000

# Run uvicorn; since main.py is now in /app, use "main:app"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
