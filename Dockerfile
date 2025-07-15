# Use Python 3.11 base image (has distutils - fixes Railway Python 3.12 issue)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel/setuptools first
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with verbose output
RUN pip install --no-cache-dir --verbose -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Create startup script that runs both services
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'echo "Starting trading backend..."' >> /app/start.sh && \
    echo 'python real_ai_backend.py &' >> /app/start.sh && \
    echo 'echo "Starting Streamlit frontend..."' >> /app/start.sh && \
    echo 'streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true' >> /app/start.sh && \
    chmod +x /app/start.sh

# Run both backend and frontend
CMD ["/app/start.sh"]