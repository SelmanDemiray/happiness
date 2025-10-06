@echo off
REM Neural Network Command Center Startup Script for Windows

echo 🚀 Starting Neural Network Command Center...

REM Create necessary directories
if not exist "cache\datasets" mkdir cache\datasets
if not exist "cache\huggingface" mkdir cache\huggingface
if not exist "models" mkdir models
if not exist "data" mkdir data

REM Set default environment variables if not set
if not defined HUGGINGFACE_TOKEN set HUGGINGFACE_TOKEN=
if not defined BACKEND_PORT set BACKEND_PORT=55320
if not defined FRONTEND_PORT set FRONTEND_PORT=55321
if not defined PYTHON_SERVICE_PORT set PYTHON_SERVICE_PORT=55322
if not defined INFERENCE_SERVICE_PORT set INFERENCE_SERVICE_PORT=55323
if not defined DATABASE_URL set DATABASE_URL=sqlite:./data/inference.db

echo 📁 Created necessary directories
echo 🔧 Environment variables set
echo 🐳 Starting Docker services...

REM Start all services
docker-compose up --build -d

echo ✅ All services started!
echo.
echo 🌐 Access your applications:
echo   • Frontend: http://localhost:55321
echo   • Backend API: http://localhost:55320
echo   • Python Service: http://localhost:55322
echo   • Inference Service: http://localhost:55323
echo.
echo 📊 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
