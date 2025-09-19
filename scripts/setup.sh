#!/bin/bash

# SOC Portal Setup Script
echo "🚀 SOC Portal Setup Script"
echo "=========================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   Press Enter when ready to continue..."
    read
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p attachments
mkdir -p logs

# Start development environment
echo "🐳 Starting development environment..."
docker-compose up -d db kc-db keycloak

echo "⏳ Waiting for services to start..."
sleep 10

echo "✅ Setup complete!"
echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   Keycloak: http://localhost:8080"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Next steps:"
echo "   1. Configure Keycloak realm and roles"
echo "   2. Update .env with your SMTP settings"
echo "   3. Start backend: cd app && uvicorn app.main:app --reload"
echo "   4. Start frontend: cd frontend && npm run dev"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"






