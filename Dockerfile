FROM python:3.10.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unrar-free \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY fonts/* /usr/share/fonts/truetype/custom/

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# RUN python -m nltk.downloader punkt
# RUN python -m nltk.downloader stopwords

WORKDIR /app

