# =========================================================================
# Backend Dockerfile — Cybergy Talent FastAPI service
# Multi-stage-free but security-conscious: runs as a NON-ROOT user.
# =========================================================================

# Pin a slim, specific Python base image for small size + reproducibility.
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System packages required by some Python libs:
#   * libmagic1 for python-magic (MIME sniffing)
#   * build tools are avoided by using wheels; add if a source build is needed.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Create a dedicated non-root user and group to run the app (DevSecOps).
RUN groupadd --system app && useradd --system --gid app --home /app app

WORKDIR /app

# Install dependencies first (leverages Docker layer caching).
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application source.
COPY . .

# Ensure the storage directory exists and is owned by the app user.
RUN mkdir -p /app/storage && chown -R app:app /app

# Drop privileges: everything below runs as the unprivileged 'app' user.
USER app

EXPOSE 8000

# Basic container healthcheck hitting the /health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/health').status==200 else sys.exit(1)"

# Start the ASGI server. Use multiple workers in production via env if desired.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
