# -----------------------
# Stage 1: Builder
# -----------------------
FROM python:3.11-slim as builder

WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

# -----------------------
# Stage 2: Runtime
# -----------------------
FROM python:3.11-slim

# Set timezone to UTC
ENV TZ=UTC
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        cron \
        tzdata \
    && ln -snf /usr/share/zoneinfo/UTC /etc/localtime \
    && echo "UTC" > /etc/timezone \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app.py ./ 
COPY keys/ ./keys/
COPY scripts/ ./scripts/

# Copy cron file
COPY cron/2fa-cron /etc/cron.d/my-cron
RUN chmod 0644 /etc/cron.d/my-cron \
    && crontab /etc/cron.d/my-cron

# Create volume mount points
RUN mkdir -p /data /cron \
    && chmod 755 /data /cron

# Expose port
EXPOSE 8080

# Start cron and FastAPI server
CMD ["sh", "-c", "cron && uvicorn app:app --host 0.0.0.0 --port 8080"]
