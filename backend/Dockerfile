FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root

COPY . .
COPY start.sh .
COPY run.sh .

RUN chmod +x start.sh

EXPOSE 8000

RUN ["./run.sh"]
CMD ["./start.sh"]
