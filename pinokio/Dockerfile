# Pinokio Web Interface for KeikenV
FROM node:18-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    python3-pip \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create package.json for our Pinokio web interface
COPY package.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY server.js ./
COPY public/ ./public/

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8900

# Start the service
CMD ["node", "server.js"]