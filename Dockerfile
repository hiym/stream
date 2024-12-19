FROM python:3.11-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    chromium-driver \
    chromium \
    libnss3 \
    ffmpeg \
    && apt-get clean

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем скрипт
COPY script.py /app/script.py
WORKDIR /app

# Установка Streamlink
RUN pip install streamlink

CMD ["python", "script.py"]
