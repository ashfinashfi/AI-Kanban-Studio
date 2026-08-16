# Stage 1: Build Next.js Static Site
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI Backend with uv
FROM python:3.11-slim
WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set Python path to /app so `backend` module is importable from anywhere
ENV PYTHONPATH=/app

# Copy backend dependencies definition and install with uv
COPY backend/pyproject.toml ./backend/
RUN uv pip install --system -r backend/pyproject.toml

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend static assets from Stage 1 into backend/static
COPY --from=frontend-builder /app/frontend/out ./backend/static

EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
