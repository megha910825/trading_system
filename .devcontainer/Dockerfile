# ─────────────────────────────────────────────────────────────────────────────
# Trading System — Dev Container Image
# Base: Microsoft's Python 3.11 devcontainer image (Debian Bookworm)
# ─────────────────────────────────────────────────────────────────────────────
FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm

# System packages needed by some Python wheels (ta-lib, matplotlib, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        curl \
        git \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set timezone to Europe/Berlin (matches the trading system default)
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Upgrade pip once at build time
# --break-system-packages is required on Debian Bookworm (PEP 668)
# --trusted-host flags bypass SSL cert verification failures caused by corporate proxies
RUN pip install --upgrade pip --break-system-packages \
        --trusted-host pypi.org \
        --trusted-host pypi.python.org \
        --trusted-host files.pythonhosted.org

# Copy only requirements first so Docker layer-caches the install step
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages \
        --trusted-host pypi.org \
        --trusted-host pypi.python.org \
        --trusted-host files.pythonhosted.org \
        -r /tmp/requirements.txt

# Working directory (devcontainer mounts the repo here automatically)
WORKDIR /workspaces/trading_system
