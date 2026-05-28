# ─────────────────────────────────────────────────────────────────────────────
# Trading System — Production Image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim-bookworm

# System dependencies required by Python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        curl \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

# Timezone
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Non-root user for security
RUN useradd --create-home --shell /bin/bash trader
WORKDIR /app

# Install Python dependencies (cached layer)
# --trusted-host flags bypass SSL cert verification failures caused by corporate proxies
COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir \
        --trusted-host pypi.org \
        --trusted-host pypi.python.org \
        --trusted-host files.pythonhosted.org \
 && pip install --no-cache-dir -r requirements.txt \
        --trusted-host pypi.org \
        --trusted-host pypi.python.org \
        --trusted-host files.pythonhosted.org

# Copy application source
COPY --chown=trader:trader . .

# Create runtime directories
RUN mkdir -p data/fundamentals_cache data/earnings_cache data/insider_cache logs cache \
 && chown -R trader:trader data logs cache

# Copy and enable entrypoint
COPY --chown=trader:trader entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER trader

# Streamlit listens on 8501
EXPOSE 8501

ENTRYPOINT ["/entrypoint.sh"]
# Default: run the dashboard
CMD ["dashboard"]
