# 🚀 Neural Network Command Center (NNCC) - Enhanced with Dataset Management

A comprehensive deep learning platform that seamlessly integrates Hugging Face datasets with neural network training capabilities. This enhanced version provides a unified interface for dataset discovery, preview, download, and training initialization.

## 🌟 Key Features

### Core Neural Network Training
- **Architecture Designer**: Visual neural network builder with drag-and-drop interface
- **Real-time Training**: Live monitoring with metrics, graphs, and progress tracking
- **Model Management**: Import/export models, version control, and deployment
- **Multiple Optimizers**: SGD, Adam, and more with customizable learning rates
- **Loss Functions**: MSE, Cross-Entropy, and other standard loss functions

### 🆕 Enhanced Dataset Management
- **Hugging Face Integration**: Direct access to thousands of datasets
- **Curated Gallery**: Pre-loaded popular datasets (MNIST, CIFAR-10, ImageNet, etc.)
- **Advanced Search**: Filter by modality, license, language, and task categories
- **Dataset Preview**: Interactive data inspection with configurable sample sizes
- **Smart Download**: Progress tracking, caching, and format conversion
- **Transformation Pipeline**: Automatic preprocessing for trainer compatibility

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Rust Backend  │    │ Python Service  │
│   (React/HTML)  │◄──►│   (Axum)        │◄──►│ (FastAPI)       │
│   Port: 55321   │    │   Port: 55320   │    │ Port: 55322     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   SQLite DB     │    │ Hugging Face    │
│   (Static)      │    │   (Models)      │    │ Hub & Datasets  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Hugging Face account and token (optional but recommended)

### 1. Environment Setup
```bash
# Copy and configure environment variables
cp .env.example .env

# Edit .env file with your settings
HUGGINGFACE_TOKEN=your_token_here
BACKEND_PORT=55320
FRONTEND_PORT=55321
PYTHON_SERVICE_PORT=55322
```

### 2. Launch the System
```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 3. Access the Interface
- **Frontend**: http://localhost:55321
- **Backend API**: http://localhost:55320
- **Python Service**: http://localhost:55322

## 📊 Dataset Management Workflow

### 1. Discovery
- **Curated Gallery**: Browse pre-loaded popular datasets
- **Search**: Find datasets by name, description, or tags
- **Filters**: Narrow down by modality, license, language, etc.

### 2. Preview
- **Interactive Inspection**: View sample data with configurable size
- **Column Analysis**: Understand data structure and types
- **Split Selection**: Choose train/validation/test splits
- **Format Detection**: Automatic handling of images, text, audio

### 3. Download
- **Smart Caching**: Local storage with progress tracking
- **Sampling Options**: Download full dataset or samples
- **Format Conversion**: Automatic conversion for trainer compatibility
- **Size Management**: Configurable limits and compression

### 4. Training Integration
- **Seamless Import**: Direct integration with training pipeline
- **Data Validation**: Automatic compatibility checks
- **Preprocessing**: Built-in transformations for common formats

## 🔧 Configuration

### Environment Variables
```bash
# Backend Configuration
BACKEND_PORT=55320
FRONTEND_PORT=55321

# Hugging Face Integration
HUGGINGFACE_TOKEN=your_token_here
HUGGINGFACE_CACHE_DIR=./cache/huggingface

# Python Service
PYTHON_SERVICE_PORT=55322
PYTHON_SERVICE_HOST=localhost

# Dataset Configuration
DATASET_CACHE_DIR=./cache/datasets
MAX_DATASET_SIZE_MB=1000
DEFAULT_SAMPLE_SIZE=1000

# Training Configuration
DEFAULT_EPOCHS=10
DEFAULT_BATCH_SIZE=32
DEFAULT_LEARNING_RATE=0.001
```

### API Endpoints

#### Dataset Management
- `GET /datasets/curated` - Get curated popular datasets
- `GET /datasets/search?query=...` - Search datasets
- `GET /datasets/{id}/preview` - Preview dataset samples
- `POST /datasets/{id}/download` - Download dataset
- `GET /datasets/{id}/configs` - Get dataset configurations
- `POST /datasets/{id}/transform` - Transform dataset

#### Neural Network Training
- `POST /models` - Create new model
- `GET /models` - List all models
- `POST /models/{id}/train` - Start training
- `GET /models/{id}/train-stream` - Real-time training updates
- `POST /models/{id}/predict` - Make predictions

## 🎯 Use Cases

### Quick Prototyping
1. Browse curated datasets
2. Preview data structure
3. Download sample
4. Design neural network
5. Start training immediately

### Advanced Research
1. Search specific datasets
2. Apply custom filters
3. Download full datasets
4. Apply transformations
5. Train complex models

### Production Deployment
1. Use production datasets
2. Implement data pipelines
3. Monitor training metrics
4. Export trained models
5. Deploy to production

## 🔒 Security Features

- **Token Management**: Secure Hugging Face authentication
- **Environment Isolation**: Docker containerization
- **Data Privacy**: Local caching and processing
- **Access Control**: Configurable API endpoints

## 📈 Performance Optimizations

- **Streaming**: Large dataset handling with streaming
- **Caching**: Intelligent local caching system
- **Compression**: Automatic data compression
- **Parallel Processing**: Multi-threaded operations
- **Memory Management**: Efficient memory usage

## 🛠️ Development

### Backend (Rust)
```bash
cd backend
cargo run
```

### Python Service
```bash
cd python_service
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
# Serve with any static server
python -m http.server 55321
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Hugging Face**: For providing the datasets and hub infrastructure
- **Rust Community**: For the excellent Axum web framework
- **Python Community**: For FastAPI and datasets libraries
- **Docker**: For containerization support

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API endpoints
- Test with the provided examples

---

**Happy Training! 🚀**
