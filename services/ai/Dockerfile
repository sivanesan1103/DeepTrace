FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install poetry && poetry export -f requirements.txt --output requirements.txt && pip install -r requirements.txt

COPY src/ ./src/
COPY templates/ ./templates/

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "deeptrace_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]