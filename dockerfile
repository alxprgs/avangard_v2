FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY .env /app/.env
RUN export $(cat /app/.env | xargs) && echo "PORT=${PORT}"

ENV PORT=${PORT}

EXPOSE ${PORT}

CMD ["python", "run.py"]
