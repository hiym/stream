#!/bin/bash

# 1. Сборка Docker-образа
docker build -t kick-stream-recorder .

# 2. Запуск контейнера
docker run -d --name kick-stream-recorder \
    --restart always \
    -v "$(pwd)/output:/app/output" \
    kick-stream-recorder
