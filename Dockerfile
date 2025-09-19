# ---- Backend (FastAPI) ----
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Системные зависимости для сборки популярных пакетов:
# - libpq-dev: psycopg2
# - build-essential, gcc/g++: bcrypt, uvloop и т.п.
# - libffi-dev, libssl-dev: крипто-библиотеки
# - libjpeg-dev, zlib1g-dev: Pillow
# - rustc, cargo: orjson и некоторые крипто-пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make \
    libpq-dev libffi-dev libssl-dev \
    libjpeg-dev zlib1g-dev \
    rustc cargo git curl \
  && rm -rf /var/lib/apt/lists/*

# Обновим инструменты сборки Python
RUN pip install --upgrade pip setuptools wheel

WORKDIR /app

# сначала ставим зависимости — чтобы кэшировалось
COPY requirements.txt .
RUN pip install -r requirements.txt

# затем копируем весь код
COPY . .

EXPOSE 8000
# подставь свой модуль/приложение, если отличается
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
