FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root --without dev

COPY . .

RUN chmod +x start.sh run.sh

EXPOSE 8000

CMD ["./start.sh"]
