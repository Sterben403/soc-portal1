.PHONY: help install dev prod test lint clean

help: ## Show this help message
	@echo "SOC Portal - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "🐍 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "📦 Installing Node.js dependencies..."
	cd frontend && npm install && cd ..

dev: ## Start development environment
	@echo "🚀 Starting development environment..."
	docker-compose up -d db kc-db keycloak
	@echo "⏳ Waiting for services to start..."
	sleep 10
	@echo "✅ Development environment ready!"
	@echo "🌐 Access points:"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Backend API: http://localhost:8000"
	@echo "   Keycloak: http://localhost:8080"

prod: ## Start production environment
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

test: ## Run all tests
	@echo "🧪 Running backend tests..."
	pytest app/tests/ -v --cov=app --cov-report=html
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false && cd ..

test-backend: ## Run backend tests only
	@echo "🧪 Running backend tests..."
	pytest app/tests/ -v --cov=app --cov-report=html

test-frontend: ## Run frontend tests only
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false && cd ..

lint: ## Run linting
	@echo "🔍 Running backend linting..."
	black --check --diff app/
	isort --check-only --diff app/
	mypy app/
	@echo "🔍 Running frontend linting..."
	cd frontend && npm run lint && cd ..

lint-fix: ## Fix linting issues
	@echo "🔧 Fixing backend linting issues..."
	black app/
	isort app/
	@echo "🔧 Fixing frontend linting issues..."
	cd frontend && npm run lint -- --fix && cd ..

build: ## Build production images
	@echo "🏗️ Building production images..."
	docker-compose -f docker-compose.prod.yml build

logs: ## Show logs
	docker-compose logs -f

stop: ## Stop all services
	docker-compose down

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

migrate: ## Run database migrations
	@echo "🗄️ Running database migrations..."
	alembic upgrade head

migrate-create: ## Create new migration
	@echo "📝 Creating new migration..."
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

setup: ## Initial setup
	@echo "🚀 Running initial setup..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "⚠️  Please edit .env file with your configuration"; \
	fi
	$(MAKE) install
	$(MAKE) dev
	@echo "✅ Setup complete!"

health: ## Check service health
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Backend not responding"
	@curl -f http://localhost:5173 || echo "❌ Frontend not responding"
	@curl -f http://localhost:8080 || echo "❌ Keycloak not responding"






