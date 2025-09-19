# SOC Portal - Система управления инцидентами безопасности

Современная веб-платформа для управления инцидентами информационной безопасности с поддержкой RBAC, уведомлений и аналитики.

## 🚀 Возможности

- **Управление инцидентами**: Создание, отслеживание и закрытие инцидентов
- **RBAC система**: Роли client, analyst, manager, admin с разграничением доступа
- **Уведомления**: Email, Telegram, Webhook с ретраями и логированием
- **Аналитика**: KPI, SLA метрики, уровень угроз
- **Безопасность**: CSRF защита, шифрование файлов, безопасные заголовки
- **Отчеты**: Генерация PDF, CSV, Excel отчетов
- **Keycloak интеграция**: Единая точка входа и аутентификации

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Keycloak      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Auth)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   (Database)    │
                       └─────────────────┘
```

## 🛠️ Технологии

### Backend
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **PostgreSQL** - основная база данных
- **Keycloak** - аутентификация и авторизация
- **AES-GCM** - шифрование файлов

### Frontend
- **React 18** - пользовательский интерфейс
- **TypeScript** - типизация
- **Bootstrap 5** - UI компоненты
- **Vite** - сборка и разработка

### DevOps
- **Docker** - контейнеризация
- **Kubernetes** - оркестрация
- **Nginx** - обратный прокси
- **Let's Encrypt** - SSL сертификаты

## 📋 Требования

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-org/soc-portal.git
cd soc-portal
```

### 2. Настройка переменных окружения

```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Запуск в режиме разработки

```bash
# Запуск всех сервисов
docker-compose up -d

# Или запуск только базы данных
docker-compose up -d db kc-db keycloak

# Запуск backend
cd app && uvicorn app.main:app --reload

# Запуск frontend
cd frontend && npm install && npm run dev
```

### 4. Доступ к приложению

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Keycloak**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs

## 🔧 Конфигурация

### Переменные окружения

Основные переменные в `.env`:

```env
# Backend
SECRET_KEY=your-super-secret-key
CSRF_SECRET=your-csrf-secret
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Keycloak
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=your-password
KC_DB_USER=keycloak
KC_DB_PASS=your-keycloak-db-password

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# Security
ENCRYPTION_KEY=your-32-byte-encryption-key
```

### Настройка Keycloak

1. Войдите в Keycloak Admin Console
2. Создайте realm "soc-portal"
3. Создайте клиента с настройками:
   - Client ID: `soc-portal`
   - Client Protocol: `openid-connect`
   - Access Type: `public`
   - Valid Redirect URIs: `http://localhost:5173/*`
4. Создайте роли: `client`, `analyst`, `manager`, `admin`
5. Создайте пользователей и назначьте роли

## 🚀 Продакшен развертывание

### Docker Compose (Продакшен)

```bash
# Создание .env.prod с продакшен настройками
cp env.example .env.prod

# Запуск продакшен стека
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Kubernetes

```bash
# Создание namespace
kubectl apply -f k8s/namespace.yaml

# Создание секретов (замените значения)
kubectl apply -f k8s/secret.yaml

# Применение конфигурации
kubectl apply -f k8s/configmap.yaml

# Развертывание приложения
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

### Настройка SSL сертификатов

Для автоматического получения SSL сертификатов:

```bash
# Установка cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Создание ClusterIssuer для Let's Encrypt
kubectl apply -f k8s/cluster-issuer.yaml
```

## 🔒 Безопасность

### Реализованные меры безопасности

- ✅ **CSRF защита** - Double Submit Cookie
- ✅ **Шифрование файлов** - AES-GCM
- ✅ **Безопасные заголовки** - CSP, HSTS, X-Frame-Options
- ✅ **Rate limiting** - Ограничение запросов
- ✅ **RBAC** - Разграничение доступа по ролям
- ✅ **TLS 1.3** - Современное шифрование
- ✅ **Non-root контейнеры** - Безопасность Docker

### Рекомендации по безопасности

1. **Регулярно обновляйте зависимости**
2. **Используйте сильные пароли**
3. **Настройте мониторинг безопасности**
4. **Включите WAF (ModSecurity)**
5. **Настройте резервное копирование**

## 📊 Мониторинг и логирование

### Health Checks

```bash
# Проверка состояния backend
curl http://localhost:8000/health

# Проверка состояния frontend
curl http://localhost:5173
```

### Логи

```bash
# Просмотр логов backend
docker-compose logs backend

# Просмотр логов frontend
docker-compose logs frontend

# Просмотр логов Keycloak
docker-compose logs keycloak
```

## 🧪 Тестирование

### Backend тесты

```bash
# Установка зависимостей для тестов
pip install pytest pytest-asyncio

# Запуск тестов
pytest app/tests/ -v

# Запуск с покрытием
pytest app/tests/ --cov=app --cov-report=html
```

### Frontend тесты

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск тестов
npm test

# Запуск с покрытием
npm test -- --coverage
```

## 🔄 CI/CD

Проект включает GitHub Actions pipeline:

- ✅ **Linting** - Проверка кода
- ✅ **Testing** - Автоматические тесты
- ✅ **Security scanning** - Trivy vulnerability scanner
- ✅ **Docker builds** - Сборка образов
- ✅ **Deployment** - Автоматический деплой

## 📈 Метрики и KPI

### Доступные метрики

- **SLA метрики**: Среднее время ответа и решения
- **Уровень угроз**: Агрегация по инцидентам
- **Статистика инцидентов**: По статусам, приоритетам, дням
- **Активность пользователей**: По ролям и действиям

### API эндпоинты

```bash
# SLA метрики
GET /api/slametrics

# Уровень угроз
GET /api/threat-level?period_days=30

# Статистика инцидентов
GET /api/incident-stats?period_days=30
```

## 🤝 Участие в разработке

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🆘 Поддержка

- **Документация**: [Wiki](https://github.com/your-org/soc-portal/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/soc-portal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/soc-portal/discussions)

## 📋 Чек-лист развертывания

### Безопасность
- [ ] Изменены все секретные ключи
- [ ] Настроен HTTPS/TLS
- [ ] Включены безопасные заголовки
- [ ] Настроен WAF (опционально)
- [ ] Настроено резервное копирование

### Мониторинг
- [ ] Настроены health checks
- [ ] Настроено логирование
- [ ] Настроены алерты
- [ ] Настроен мониторинг производительности

### Производительность
- [ ] Настроено кэширование
- [ ] Настроена компрессия (gzip/brotli)
- [ ] Настроена CDN (опционально)
- [ ] Настроено масштабирование

---

**SOC Portal** - Современное решение для управления инцидентами информационной безопасности.






