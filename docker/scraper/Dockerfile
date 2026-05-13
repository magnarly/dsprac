# Scraper Dockerfile - Web Scraping Service
FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY scraper/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scraper code
COPY scraper/ ./scraper/

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "scraper.main:app", "--host", "0.0.0.0", "--port", "8001"]
