# Use the official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Playwright
# We install curl to download the key, and other basic tools
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# MAGICAL STEP: Install Playwright browsers and system dependencies
# This installs Chromium and all the linux libs needed to run it
RUN playwright install chromium
RUN playwright install-deps

# Copy the actual app code
COPY . .

# Expose the port Railway uses (variable PORT)
ENV PORT=8080
EXPOSE 8080

# Start the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
