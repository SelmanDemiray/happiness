#!/bin/bash

# Neural Network Command Center Startup Script

echo "🚀 Starting Neural Network Command Center..."

# Create necessary directories
mkdir -p cache/datasets
mkdir -p cache/huggingface
mkdir -p models
mkdir -p data

# Set default environment variables if not set
export HUGGINGFACE_TOKEN=${HUGGINGFACE_TOKEN:-""}
export BACKEND_PORT=${BACKEND_PORT:-55320}
export FRONTEND_PORT=${FRONTEND_PORT:-55321}
export PYTHON_SERVICE_PORT=${PYTHON_SERVICE_PORT:-55322}
export INFERENCE_SERVICE_PORT=${INFERENCE_SERVICE_PORT:-55323}
export DATABASE_URL=${DATABASE_URL:-"sqlite:./data/inference.db"}

echo "📁 Created necessary directories"
echo "🔧 Environment variables set"
echo "🐳 Starting Docker services..."

# Start all services
docker-compose up --build -d

echo "✅ All services started!"
echo ""
echo "🌐 Access your applications:"
echo "  • Frontend: http://localhost:55321"
echo "  • Backend API: http://localhost:55320"
echo "  • Python Service: http://localhost:55322"
echo "  • Inference Service: http://localhost:55323"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
