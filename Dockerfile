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
COPY <<EOF /app/start.sh
#!/bin/bash
echo "Starting trading backend..."
python real_ai_backend.py &
BACKEND_PID=$!

echo "Starting Streamlit frontend..."
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF

RUN chmod +x /app/start.sh

# Run both backend and frontend
CMD ["/app/start.sh"]