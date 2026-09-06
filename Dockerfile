FROM ghcr.io/astral-sh/uv:0.11.8-python3.13-trixie-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY src ./src

EXPOSE 9000

CMD ["python", "src/manage.py", "runserver", "0.0.0.0:9000"]