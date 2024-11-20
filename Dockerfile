FROM python:3.10.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=Asia/Ho_Chi_Minh

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unrar-free \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Optional: Add fonts if necessary
COPY fonts/* /usr/share/fonts/truetype/custom/

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app

# Ensure the directory exists before creating the file
RUN mkdir -p /opt/voicevox_engine && \
    touch /opt/voicevox_engine/presets.yaml && \
    chmod 666 /opt/voicevox_engine/presets.yaml
