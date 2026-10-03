FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY data/ ./data/

RUN python -m pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 app \
    && mkdir /reports \
    && chown app:app /reports

USER app

ENTRYPOINT ["misconduct-mvp"]
CMD ["--input", "/app/data/demo_cases.csv", "--output", "/reports"]
