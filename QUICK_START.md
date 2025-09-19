# 🚀 Быстрый запуск SOC Portal

## 📋 Требования

- **Docker & Docker Compose** - для контейнеризации
- **Python 3.11+** - для backend
- **Node.js 18+** - для frontend
- **Git** - для клонирования репозитория

## ⚡ Быстрый старт (5 минут)

### 1. Клонирование и настройка

```bash
# Клонировать репозиторий
git clone <your-repo-url>
cd soc-portal

# Автоматическая настройка (Linux/Mac)
chmod +x scripts/setup.sh
./scripts/setup.sh

# Или для Windows
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1

# Или вручную
cp env.example .env
# Отредактировать .env файл
```

### 2. Запуск сервисов

```bash
# Запуск базы данных и Keycloak
docker-compose up -d db kc-db keycloak

# Или используя Makefile
make dev
```

### 3. Запуск приложений

```bash
# Terminal 1: Backend
cd app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 4. Доступ к приложению

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Keycloak**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs

## 🔧 Полезные команды

```bash
# Показать все доступные команды
make help

# Установка зависимостей
make install

# Запуск тестов
make test

# Проверка линтера
make lint

# Просмотр логов
make logs

# Остановка сервисов
make stop

# Проверка здоровья сервисов
make health
```

## ⚙️ Настройка Keycloak

1. Откройте http://localhost:8080
2. Войдите в Admin Console (admin/admin)
3. Создайте realm "soc-portal"
4. Создайте клиента:
   - Client ID: `soc-portal`
   - Client Protocol: `openid-connect`
   - Access Type: `public`
   - Valid Redirect URIs: `http://localhost:5173/*`
5. Создайте роли: `client`, `analyst`, `manager`, `admin`
6. Создайте пользователей и назначьте роли

## 🔒 Настройка безопасности

Отредактируйте `.env` файл:

```env
# Обязательные настройки
SECRET_KEY=your-super-secret-key-change-this
CSRF_SECRET=your-csrf-secret-change-this
ENCRYPTION_KEY=your-32-byte-encryption-key

# SMTP для уведомлений (опционально)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Telegram Bot (опционально)
TELEGRAM_BOT_TOKEN=your-bot-token
```

## 🐛 Устранение неполадок

### Проблема: Порт занят
```bash
# Проверить что использует порт
lsof -i :8000
lsof -i :5173
lsof -i :8080

# Остановить процесс
kill -9 <PID>
```

### Проблема: База данных не подключается
```bash
# Проверить статус контейнеров
docker-compose ps

# Перезапустить базу данных
docker-compose restart db

# Проверить логи
docker-compose logs db
```

### Проблема: Keycloak не запускается
```bash
# Проверить логи Keycloak
docker-compose logs keycloak

# Перезапустить Keycloak
docker-compose restart keycloak
```

## 📊 Мониторинг

```bash
# Проверка здоровья сервисов
make health

# Просмотр логов в реальном времени
make logs

# Статистика контейнеров
docker stats
```

## 🚀 Продакшен развертывание

```bash
# Создать продакшен конфигурацию
cp env.example .env.prod
# Отредактировать .env.prod

# Запустить продакшен
make prod

# Или через Docker Compose
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## 📞 Поддержка

- **Документация**: [README.md](README.md)
- **Отчет о статусе**: [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)
- **Issues**: Создайте issue в репозитории

---

**Время на полный запуск: 5-10 минут**






