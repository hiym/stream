#!/bin/bash

# Обновление системы
echo "Обновляем систему..."
sudo pacman -Syu --noconfirm

# Установка базовых зависимостей
echo "Устанавливаем базовые инструменты..."
sudo pacman -S --noconfirm python python-pip python-virtualenv curl wget git ffmpeg

# Установка Streamlink из AUR
echo "Устанавливаем Streamlink..."
yay -S --noconfirm streamlink

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
