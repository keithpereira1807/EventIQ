# ====================================================================
# EventIQ: Full-Stack Container (React Frontend + FastAPI ML Backend)
# ====================================================================

# Step 1: Build React 19 Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Step 2: Build Python FastAPI + Sentence-Transformers Backend
FROM python:3.12-slim

# Install system dependencies (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code, dataset, evaluations, and docs
COPY backend/ ./backend
COPY data/ ./data
COPY evaluation/ ./evaluation
COPY docs/ ./docs

# Copy built frontend assets from Step 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose default port
EXPOSE 8000

# Start server using dynamic $PORT (defaulting to 8000)
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
