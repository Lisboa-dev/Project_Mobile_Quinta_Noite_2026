FROM python:3.11-slim

WORKDIR /app

ENV POETRY_REQUESTS_TIMEOUT=120 \
    POETRY_INSTALLER_MAX_WORKERS=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry config installer.max-workers 1 \
    && poetry install --no-interaction --no-ansi --no-root

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
