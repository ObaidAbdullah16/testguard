# Build image from slim Python base
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Train the model at build time so the container starts instantly
RUN python train.py

EXPOSE 5000

# Use gunicorn in production (2 workers is fine for a demo)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
