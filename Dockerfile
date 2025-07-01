# Use the official Python image
FROM python:3.12.1-slim

# Set the working directory
WORKDIR /app

# Install necessary packages for OpenSSL
RUN apt-get update && apt-get install -y \
    openssl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt into the container
COPY requirements.txt .

# Install dependencies using pip without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into the container
COPY . .

# Generate self-signed SSL certificates
RUN openssl req -x509 -newkey rsa:2048 -keyout /etc/ssl/private/key.pem -out /etc/ssl/certs/cert.pem -days 365 -nodes -subj "/CN=vmi2151155.contaboserver.net"

# Expose port 5000
EXPOSE 5000

# Command to run the application using Uvicorn with SSL
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--ssl-keyfile", "/etc/ssl/private/key.pem", "--ssl-certfile", "/etc/ssl/certs/cert.pem"]