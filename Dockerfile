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
COPY pyproject.toml uv.lock ./
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
RUN mkdir -p corpus/raw
RUN curl -fsSL \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/adoption_of_children_act_2022.pdf" -o corpus/raw/adoption_of_children_act_2022.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/banking_act_1970.pdf" -o corpus/raw/banking_act_1970.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/broadcasting_act_1994.pdf" -o corpus/raw/broadcasting_act_1994.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/civil_law_act_1909.pdf" -o corpus/raw/civil_law_act_1909.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/companies_act_1967.pdf" -o corpus/raw/companies_act_1967.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/computer_misuse_act_1993.pdf" -o corpus/raw/computer_misuse_act_1993.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/contracts_(rights_of_third_parties)_act_2001.pdf" -o "corpus/raw/contracts_(rights_of_third_parties)_act_2001.pdf" \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/conveyancing_and_law_of_property_act_1886.pdf" -o corpus/raw/conveyancing_and_law_of_property_act_1886.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/criminal_procedure_code_2010.pdf" -o corpus/raw/criminal_procedure_code_2010.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/customs_act_1960.pdf" -o corpus/raw/customs_act_1960.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/cybersecurity_act_2018.pdf" -o corpus/raw/cybersecurity_act_2018.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/electronic_transactions_act_2010.pdf" -o corpus/raw/electronic_transactions_act_2010.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/employment_act_1968.pdf" -o corpus/raw/employment_act_1968.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/employment_claims_act_2016.pdf" -o corpus/raw/employment_claims_act_2016.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/employment_of_foreign_manpower_act_1990.pdf" -o corpus/raw/employment_of_foreign_manpower_act_1990.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/environmental_protection_and_management_act_1999.pdf" -o corpus/raw/environmental_protection_and_management_act_1999.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/evidence_act_1893.pdf" -o corpus/raw/evidence_act_1893.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/finance_companies_act_1967.pdf" -o corpus/raw/finance_companies_act_1967.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/financial_advisers_act_2001.pdf" -o corpus/raw/financial_advisers_act_2001.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/foreign_employee_dormitories_act_2015.pdf" -o corpus/raw/foreign_employee_dormitories_act_2015.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/frustrated_contracts_act_1959.pdf" -o corpus/raw/frustrated_contracts_act_1959.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/government_proceedings_act_1956.pdf" -o corpus/raw/government_proceedings_act_1956.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/guardianship_of_infants_act_1934.pdf" -o corpus/raw/guardianship_of_infants_act_1934.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/immigration_act_1959.pdf" -o corpus/raw/immigration_act_1959.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/income_tax_act_1947.pdf" -o corpus/raw/income_tax_act_1947.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/insurance_act_1966.pdf" -o corpus/raw/insurance_act_1966.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/interpretation_act_1965.pdf" -o corpus/raw/interpretation_act_1965.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/land_acquisition_act_1966.pdf" -o corpus/raw/land_acquisition_act_1966.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/land_titles_act_1993.pdf" -o corpus/raw/land_titles_act_1993.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/legal_profession_act_1966.pdf" -o corpus/raw/legal_profession_act_1966.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/limitation_act_1959.pdf" -o corpus/raw/limitation_act_1959.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/minors_contracts_act_1987.pdf" -o corpus/raw/minors_contracts_act_1987.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/misuse_of_drugs_act_1973.pdf" -o corpus/raw/misuse_of_drugs_act_1973.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/national_servicemen_(employment)_act_1970.pdf" -o "corpus/raw/national_servicemen_(employment)_act_1970.pdf" \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/online_criminal_harms_act_2023.pdf" -o corpus/raw/online_criminal_harms_act_2023.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/payment_services_act_2019.pdf" -o corpus/raw/payment_services_act_2019.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/penal_code_1871.pdf" -o corpus/raw/penal_code_1871.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/personal_data_protection_act_2012.pdf" -o corpus/raw/personal_data_protection_act_2012.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/public_order_act_2009.pdf" -o corpus/raw/public_order_act_2009.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/registration_of_criminals_act_1949.pdf" -o corpus/raw/registration_of_criminals_act_1949.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/retirement_and_re-employment_act_1993.pdf" -o corpus/raw/retirement_and_re-employment_act_1993.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/road_traffic_act_1961.pdf" -o corpus/raw/road_traffic_act_1961.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/sale_of_goods_act_1979.pdf" -o corpus/raw/sale_of_goods_act_1979.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/securities_and_futures_act_2001.pdf" -o corpus/raw/securities_and_futures_act_2001.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/supply_of_goods_act_1982.pdf" -o corpus/raw/supply_of_goods_act_1982.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/unfair_contract_terms_act_1977.pdf" -o corpus/raw/unfair_contract_terms_act_1977.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/variable_capital_companies_act_2018.pdf" -o corpus/raw/variable_capital_companies_act_2018.pdf \
    "https://github.com/GSylph/legal_advisor_chatbot/raw/main/corpus/raw/womens_charter_1961.pdf" -o corpus/raw/womens_charter_1961.pdf

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

RUN uv run python -m src.kb_cli ingest corpus/raw/

# ── Runtime ───────────────────────────────────────────────────────────────────
EXPOSE 8000

# The StaticFiles mount in api_server.py will serve frontend/dist automatically.
CMD ["uv", "run", "uvicorn", "src.api_server:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1"]
