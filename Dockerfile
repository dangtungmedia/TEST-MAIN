FROM python:3.10.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install necessary packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    unrar-free \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .  # Copy requirements file to container
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files to the container's working directory
COPY . .  # Corrected COPY command

# Set working directory
WORKDIR /app

# Ensure download.sh is executable and run it
RUN chmod +x /app/download.sh && /app/download.sh
