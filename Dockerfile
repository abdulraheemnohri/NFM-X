# NFM-X Dockerfile
# Multi-stage build for production and development

# Build stage
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.10-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash nfmuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/nfmuser/.local

# Make sure scripts in .local are usable
ENV PATH=/home/nfmuser/.local/bin:$PATH

# Copy application code
COPY --chown=nfmuser:nfmuser . .

# Create necessary directories
RUN mkdir -p /app/data /app/storage /app/uploads /app/logs

# Set permissions
RUN chown -R nfmuser:nfmuser /app

# Switch to non-root user
USER nfmuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3     CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()" || exit 1

# Run the application
CMD ["python", "-m", "backend.app.main"]