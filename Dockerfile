FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && curl -fsSL https://github.com/cloudflare/cloudflared/releases/download/2026.6.0/cloudflared-linux-amd64 \
       -o /usr/local/bin/cloudflared \
    && chmod +x /usr/local/bin/cloudflared \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

COPY app/ ./app/
COPY run.sh ./run.sh
RUN chmod +x ./run.sh

EXPOSE 8000

CMD ["./run.sh"]
