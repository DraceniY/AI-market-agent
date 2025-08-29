FROM python:3.10-slim

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip 

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . /app/

# Environment variables
ENV PYTHONPATH=/app/src
ENV OTEL_TRACES_EXPORTER=console
ENV OTEL_METRICS_EXPORTER=console
ENV OTEL_LOGS_EXPORTER=console
ENV OTEL_SERVICE_NAME=ecommerce-multi-agent
ENV OTEL_RESOURCE_ATTRIBUTES=service.version=1.0.0,deployment.environment=docker

# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 5000 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run main orchestrator
CMD ["python", "src/main.py", "Adidas Samba sneakers", "--no-browser"]
