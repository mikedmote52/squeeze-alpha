FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Copy the server file
COPY server.py .

# Expose the port
EXPOSE 10000

# Run the server
CMD ["python", "server.py"]