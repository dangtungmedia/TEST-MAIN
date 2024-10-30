FROM python:3.10.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# RUN python -m nltk.downloader punkt
# RUN python -m nltk.downloader stopwords

WORKDIR /app

# Copy download.sh vào container tại thư mục /app
COPY download.sh /app/download.sh

# Cấp quyền thực thi cho download.sh
RUN chmod +x /app/download.sh

# Chạy download.sh
RUN /app/download.sh