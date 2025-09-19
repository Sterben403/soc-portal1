FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# системные либы для сборки/работы популярных пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make \
    libffi-dev libssl-dev \
    libjpeg-dev zlib1g-dev \
    curl git \
  && rm -rf /var/lib/apt/lists/*

# апгрейд инструментов
RUN pip install --upgrade pip setuptools wheel

WORKDIR /app

# заранее ставим бинарное колесо PyYAML (чтобы ни один пакет не дотащил старую 5.x из исходников)
RUN pip install --only-binary=:all: PyYAML==6.0.2

# зависимости → кэш слоя
COPY requirements.txt .
RUN pip install -r requirements.txt

# код
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
