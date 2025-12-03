FROM python:3.11-slim

WORKDIR /app

# Install cron and timezone
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy requirements then install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Ensure directories exist
RUN mkdir -p /data /cron

# Copy cron config
COPY cron/2fa-cron /cron/2fa-cron
RUN chmod 644 /cron/2fa-cron && crontab /cron/2fa-cron

EXPOSE 8080

CMD service cron start && python3 app.py
