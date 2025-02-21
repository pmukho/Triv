FROM python:3.11-slim

WORKDIR /app

COPY cache/requirements.txt .
RUN pip install -r requirements.txt pytest pytest-cov pytest-asyncio

COPY cache/ /app/cache/
COPY tests/ /app/tests/

ENV PYTHONPATH=/app

CMD ["pytest", "tests/test_game_batch.py", "-v"]