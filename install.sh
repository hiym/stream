#!/bin/bash

# Обновление системы и установка базовых инструментов
echo "Обновляем список пакетов и устанавливаем зависимости..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv curl wget git ffmpeg

# Установка Streamlink
echo "Устанавливаем Streamlink..."
sudo apt install -y streamlink

# Создание виртуального окружения
echo "Создаём виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate

# Обновление pip
echo "Обновляем pip..."
pip install --upgrade pip

# Установка зависимостей из requirements.txt
echo "Устанавливаем зависимости из requirements.txt..."
pip install -r requirements.txt

# Проверка OpenSSL
openssl_version=$(openssl version)
echo "Установлена версия OpenSSL: $openssl_version"

# Проверка Streamlink
streamlink_version=$(streamlink --version)
if [[ $? -eq 0 ]]; then
    echo "Streamlink успешно установлен. Версия: $streamlink_version"
else
    echo "Ошибка при установке Streamlink."
    exit 1
fi

# Завершение установки
echo "Установка завершена. Активируйте виртуальное окружение с помощью 'source venv/bin/activate'."
