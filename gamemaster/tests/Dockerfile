FROM python:3.11-slim

# disable build files, enable immediate stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY cache/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytest pytest-cov pytest-asyncio

COPY gamemaster/ /app/gamemaster/

ENV PYTHONPATH=/app/gamemaster

CMD ["pytest", "gamemaster/tests/", "-v"]