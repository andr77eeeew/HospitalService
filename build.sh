#!/bin/bash

# Обновляем систему и устанавливаем зависимости
apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    build-essential

# Устанавливаем Poetry
pip install poetry

# Конфигурация Poetry
export POETRY_VIRTUALENVS_IN_PROJECT=true
export POETRY_NO_INTERACTION=1

# Устанавливаем зависимости проекта
poetry install --no-root

# Собираем статические файлы
python manage.py collectstatic --noinput
