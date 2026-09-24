# Adapted from CDS212: beispiel-app/Dockerfile (base / builder / runtime).
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

FROM base AS builder
# Keep runtime dependencies in one place; copy them before application code.
COPY pyproject.toml .
RUN python -c "import pathlib,tomllib; p=tomllib.loads(pathlib.Path('pyproject.toml').read_text()); pathlib.Path('requirements.txt').write_text('\n'.join(p['project']['dependencies']))"
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM base AS runtime
RUN useradd --create-home --uid 10001 appuser

COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser wsgi.py ./

USER appuser
EXPOSE 8000

# In-memory state is process-local: keep one worker until PostgreSQL is used.
ENV GUNICORN_WORKERS=1

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; assert urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200"

# exec lets Gunicorn receive SIGTERM directly for a graceful shutdown.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:8000 --workers \"${GUNICORN_WORKERS}\" --access-logfile - --error-logfile - wsgi:app"]
