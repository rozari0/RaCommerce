# ---------- PYTHON BUILD ----------
FROM python:3.14-slim AS python-build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    curl \
    ca-certificates \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*


# uv installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT="/usr/local/"

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev -n


# ---------- FINAL RUNTIME IMAGE ----------
FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Python environment
COPY --from=python-build /usr/local /usr/local

# App source
COPY . .
