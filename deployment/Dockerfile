# Use official Python slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies (libgomp1 for LightGBM/XGBoost, build tools, libpq-dev, curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project code and pre-trained model artifacts
COPY . /app/

# Make entrypoint script executable
RUN chmod +x /app/scripts/entrypoint.sh

# Expose port (default 8000, dynamic on Railway)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run entrypoint script
CMD ["/app/scripts/entrypoint.sh"]
