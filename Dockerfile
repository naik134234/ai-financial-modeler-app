# Multi-stage Dockerfile
# 1. Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/ .
# Set env var for build (API URL will be relative path /api in prod)
ENV NEXT_PUBLIC_API_URL=
RUN npm run build

# 2. Build Backend & Serve
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies (for optional PDF/Image stuff)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Backend reqs
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend code
COPY backend/ .

# Copy Built Frontend from Stage 1 to 'static' folder
COPY --from=frontend-builder /app/frontend/out ./static

# Expose port
ENV PORT=7860
EXPOSE 7860

# Run Command (Assumes main.py is updated to serve static files)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
