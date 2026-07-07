FROM python:3.11-slim

# Tesseract + poppler are needed by the extraction pipeline's OCR fallback
# (app/ingestion/extract_pdfs.py) for scanned/image-only source PDFs.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr poppler-utils libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build context is the REPO ROOT (see docker-compose.yml `context: .` and
# render.yaml), not backend/, so that data/ (the gold dataset + source PDFs)
# can be baked into the image. Render (and most single-Dockerfile PaaS
# deploys) can't bind-mount an arbitrary host folder the way local
# docker-compose can, so the data this app is seeded from has to actually be
# part of the image rather than mounted in at runtime.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/tests ./tests
COPY data ./data

EXPOSE 8000
# Shell form (not exec form) so ${PORT} is expanded at container start. Render
# injects PORT and requires the process to bind to it; local docker-compose
# doesn't set PORT, so it falls back to 8000 to match the compose port mapping.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
