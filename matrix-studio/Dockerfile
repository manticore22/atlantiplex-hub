FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_enhanced.txt .
RUN pip install --no-cache-dir -r requirements_enhanced.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads web/templates web/static

# Set environment variables
ENV FLASK_ENV=production
ENV FLASK_APP=COMPLETE_WORKING.py
ENV HOST=0.0.0.0
ENV PORT=8081

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/api/health || exit 1

# Start the application
CMD ["python", "COMPLETE_WORKING.py"]