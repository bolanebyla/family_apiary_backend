# === Base build stage: installs deps, builds project ===
FROM python:3.13-slim AS base

# Install uv package manager (fast, modern pip replacement)
# Required for installing locked dependencies
RUN pip install uv

# Set working directory inside container
# Isolate app
WORKDIR /app

# Install system dependencies needed to build wheels for some Python packages
# Only needed for build, removed later for a smaller image
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency metadata and README (important for hatchling)
# These layers are cached to avoid re-installing on every code change
COPY pyproject.toml uv.lock README.md ./

# Install dependencies *into the system Python* using the lock file
# Non-editable install (faster and safer in production)
# `--system` installs into the base Python env, not a venv
# Then clean up to shrink the image
RUN uv pip install --system . \
  && apt-get purge -y build-essential curl \
  && rm -rf /var/lib/apt/lists/*

# Copy actual source code last (so that dependency layers are cached if code changes)
COPY src ./src

# === Final runtime image: small and clean ===
FROM python:3.13-slim AS runtime

# Copy only installed Python packages and app code from base stage
# Ensures a clean image without build tools or source cache
COPY --from=base /usr/local /usr/local
COPY --from=base /app /app

# Set working directory and Python import path
WORKDIR /app
ENV PYTHONPATH=/app/src

# Run with uvicorn
CMD ["uvicorn", "family_apiary.run.api:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080"]