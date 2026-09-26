# ==============================================================================
# Universitetet i Agder (UiA) - Controller Analytics & AI Pipeline
# Produksjons- og utviklingscontainer basert på Python 3.12 og DuckDB
# Forfatter: Frank Ellingsen (Project Controller)
# ==============================================================================

FROM python:3.12-slim

# Sett miljøvariabler
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Opprett ikke-root bruker for sikker containerkjøring
RUN groupadd -r controller && useradd -r -g controller -m -d /home/controller controller

# Installer nødvendige systemverktøy
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Sett arbeidskatalog
WORKDIR /workspace

# Kopier avhengighetskrav og installer
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    duckdb==1.5.3 \
    pandas==2.2.3 \
    openpyxl==3.1.5 \
    pyyaml==6.0.2 \
    pytest==8.3.4 \
    python-dotenv==1.0.1

# Kopier prosjektfiler
COPY --chown=controller:controller . /workspace

# Bytt til ikke-root bruker
USER controller

# Eksponer port 8000 for eventuell lokal API- eller dashboard-tjeneste
EXPOSE 8000

# Standard kommando: Kjør rapport- og forretningsregelvalidering
CMD ["python", "scripts/verify_reporting_rules.py"]
