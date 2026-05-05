FROM python:3.11-slim

WORKDIR /app

# Instala Poetry
RUN pip install --upgrade pip && pip install poetry

# Copia apenas arquivos de dependência primeiro (cache inteligente)
COPY pyproject.toml poetry.lock* ./

# Instala dependências sem criar virtualenv
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copia código
COPY . .

# Cria um usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]