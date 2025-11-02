# --- Base image with Python ---
FROM python:3.12-slim AS base

# Install dependencies needed for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Dependency layer (cached if requirements.txt unchanged) ---
FROM base AS builder
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Final runtime image ---
FROM python:3.12-slim AS final
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Don't copy app code here - it will be mounted as a volume for hot reload
# COPY app/ /app/app/

EXPOSE 8080