# ── EALAI Dockerfile ──────────────────────────────────────────────────────────
#
# Single-stage build. Node is included to compile the React frontend; it is
# not stripped out (see DEPLOY.md §8 for rationale and future optimisation).
#
# Build context must be the repo root. Run:
#   docker build -t ealai .
#   docker run -d --env-file .env -p 8000:8000 ealai
# ──────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

# ── System deps ───────────────────────────────────────────────────────────────
# nodejs + npm: needed only to build the React frontend.
# curl: used by the Railway health check probe.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nodejs \
        npm \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python package manager ────────────────────────────────────────────────────
# Install uv globally so subsequent RUN steps can call it directly.
RUN pip install --no-cache-dir uv

# ── Python dependencies ───────────────────────────────────────────────────────
# Copy lockfile + project manifest first so Docker caches this layer
# independently from application code changes.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --no-dev --frozen

# ── spaCy language model ──────────────────────────────────────────────────────
# en_core_web_sm (12 MB). See DEPLOY.md §6 for why sm not lg.
RUN uv run python -m spacy download en_core_web_sm

# ── Frontend build ────────────────────────────────────────────────────────────
# Copy package manifests first to cache npm install independently.
COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci --prefer-offline

# Copy the full frontend source and build it.
COPY frontend/ frontend/
RUN cd frontend && npm run build

# ── Application source ────────────────────────────────────────────────────────
COPY src/ src/
COPY prompts/ prompts/

# ── Knowledge base corpus ─────────────────────────────────────────────────────
# Download the 48 statute PDFs from the public GitHub repo at build time.
# This avoids pushing large binary files to HF Spaces (which requires Xet
# storage for binaries). The GitHub repo is the canonical source of the PDFs.
RUN mkdir -p corpus/raw && \
    BASE="https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw" && \
    for f in \
        adoption_of_children_act_2022.pdf \
        banking_act_1970.pdf \
        broadcasting_act_1994.pdf \
        civil_law_act_1909.pdf \
        companies_act_1967.pdf \
        computer_misuse_act_1993.pdf \
        conveyancing_and_law_of_property_act_1886.pdf \
        criminal_procedure_code_2010.pdf \
        customs_act_1960.pdf \
        cybersecurity_act_2018.pdf \
        electronic_transactions_act_2010.pdf \
        employment_act_1968.pdf \
        employment_claims_act_2016.pdf \
        employment_of_foreign_manpower_act_1990.pdf \
        environmental_protection_and_management_act_1999.pdf \
        evidence_act_1893.pdf \
        finance_companies_act_1967.pdf \
        financial_advisers_act_2001.pdf \
        foreign_employee_dormitories_act_2015.pdf \
        frustrated_contracts_act_1959.pdf \
        government_proceedings_act_1956.pdf \
        guardianship_of_infants_act_1934.pdf \
        immigration_act_1959.pdf \
        income_tax_act_1947.pdf \
        insurance_act_1966.pdf \
        interpretation_act_1965.pdf \
        land_acquisition_act_1966.pdf \
        land_titles_act_1993.pdf \
        legal_profession_act_1966.pdf \
        limitation_act_1959.pdf \
        minors_contracts_act_1987.pdf \
        misuse_of_drugs_act_1973.pdf \
        online_criminal_harms_act_2023.pdf \
        payment_services_act_2019.pdf \
        penal_code_1871.pdf \
        personal_data_protection_act_2012.pdf \
        public_order_act_2009.pdf \
        registration_of_criminals_act_1949.pdf \
        retirement_and_re-employment_act_1993.pdf \
        road_traffic_act_1961.pdf \
        sale_of_goods_act_1979.pdf \
        securities_and_futures_act_2001.pdf \
        supply_of_goods_act_1982.pdf \
        unfair_contract_terms_act_1977.pdf \
        variable_capital_companies_act_2018.pdf \
        womens_charter_1961.pdf \
    ; do \
        curl -fsSL "${BASE}/${f}" -o "corpus/raw/${f}"; \
    done && \
    curl -fsSL "${BASE}/contracts_%28rights_of_third_parties%29_act_2001.pdf" \
         -o "corpus/raw/contracts_(rights_of_third_parties)_act_2001.pdf" && \
    curl -fsSL "${BASE}/national_servicemen_%28employment%29_act_1970.pdf" \
         -o "corpus/raw/national_servicemen_(employment)_act_1970.pdf"

# ── HF Spaces user setup ──────────────────────────────────────────────────────
# Hugging Face Spaces runs containers as a non-root user (uid 1000).
# Create the user and ensure all writable paths are owned by it so that
# the audit log and vector store can be written at runtime.
RUN useradd -m -u 1000 appuser

# Ensure storage directories exist and are writable by the app user.
RUN mkdir -p storage/vector_store storage/logs \
    && chown -R appuser:appuser /app

# Switch to the non-root user for the ingestion step and all runtime commands.
USER appuser

RUN uv run python -m src.kb_cli index --path corpus/raw/

# ── Runtime ───────────────────────────────────────────────────────────────────
EXPOSE 8000

# The StaticFiles mount in api_server.py will serve frontend/dist automatically.
CMD ["uv", "run", "uvicorn", "src.api_server:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1"]
