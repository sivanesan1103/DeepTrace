FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenv.create false

COPY pyproject.toml ./
RUN poetry install --no-interaction --no-ansi --only-main

COPY src/ ./src/

EXPOSE 8000

CMD ["python", "-m", "phone_service"]