FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install PraisonAI and dependencies
RUN pip install --no-cache-dir \
    praisonai \
    praisonaiagents \
    fastapi \
    uvicorn[standard] \
    pydantic \
    requests \
    duckduckgo-search \
    python-multipart

# Copy application files
COPY . .

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]