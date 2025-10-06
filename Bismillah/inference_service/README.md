# 🤖 AI Inference Chat Service

A comprehensive inference service for the Neural Network Command Center that provides real-time chat interfaces with trained models, supporting text, image, video, and multimodal inference.

## 🌟 Features

### Core Inference Capabilities
- **Text Generation**: Chat with language models for text generation, completion, and conversation
- **Image Analysis**: Upload images for classification, object detection, and visual understanding
- **Video Processing**: Analyze video content for object tracking, scene understanding, and temporal analysis
- **Multimodal Inference**: Combine text, images, and audio for complex reasoning tasks

### Model Management
- **Model Registry**: Centralized model storage with metadata, versioning, and performance metrics
- **Dynamic Loading**: Load and unload models on-demand with memory management
- **Model Comparison**: Side-by-side comparison of model performance and capabilities
- **Smart Recommendations**: AI-powered model suggestions based on task requirements

### Chat Interface
- **Real-time WebSocket**: Live chat with typing indicators and streaming responses
- **Session Management**: Persistent chat sessions with conversation history
- **Multi-model Support**: Switch between different models within the same interface
- **Customizable Settings**: Adjust temperature, top-p, max tokens, and other parameters

### Advanced Features
- **Intelligent Caching**: LRU cache for inference results with configurable TTL
- **Batch Processing**: Process multiple inputs simultaneously for efficiency
- **Performance Monitoring**: Real-time metrics on inference time, memory usage, and accuracy
- **Error Handling**: Robust error recovery and user-friendly error messages

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │ Inference API   │    │ Model Registry │
│   (Chat UI)     │◄──►│   (Rust)        │◄──►│   (SQLite)     │
│   Port: 55321   │    │   Port: 55323   │    │                │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐               │
         │              │ Inference Engine│               │
         │              │   (Candle/Torch)│               │
         │              └─────────────────┘               │
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐               │
         │              │  Cache System   │               │
         │              │     (LRU)       │               │
         │              └─────────────────┘               │
         │                                                │
         ▼                                                ▼
┌─────────────────┐                            ┌─────────────────┐
│   WebSocket     │                            │   Model Files  │
│   (Real-time)   │                            │   (Storage)     │
└─────────────────┘                            └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Rust 1.75+ (for development)
- Python 3.8+ with PyTorch (for model loading)

### 1. Environment Setup
```bash
# Set environment variables
export INFERENCE_SERVICE_PORT=55323
export DATABASE_URL=sqlite:./data/inference.db
export RUST_LOG=info
```

### 2. Launch with Docker
```bash
# Start the inference service
docker-compose up inference-service

# Or start all services
docker-compose up --build
```

### 3. Access the Interface
- **Frontend**: http://localhost:55321
- **Inference API**: http://localhost:55323
- **WebSocket**: ws://localhost:55323/chat/{session_id}/ws

## 📊 API Endpoints

### Model Management
- `GET /models` - List all available models
- `POST /models` - Register a new model
- `GET /models/{id}` - Get model details
- `POST /models/{id}/load` - Load model into memory
- `POST /models/{id}/unload` - Unload model from memory
- `DELETE /models/{id}` - Remove model from registry

### Inference Endpoints
- `POST /inference/text` - Text generation and completion
- `POST /inference/image` - Image classification and analysis
- `POST /inference/video` - Video content analysis
- `POST /inference/multimodal` - Multimodal inference
- `POST /inference/batch` - Batch processing

### Chat Interface
- `POST /chat/start` - Start a new chat session
- `GET /chat/{session_id}/ws` - WebSocket connection
- `POST /chat/{session_id}/message` - Send message
- `GET /chat/{session_id}/history` - Get chat history
- `POST /chat/{session_id}/clear` - Clear chat history

### Model Selection
- `GET /models/search` - Search models by criteria
- `POST /models/compare` - Compare multiple models
- `POST /models/recommend` - Get model recommendations

### Cache Management
- `POST /cache/clear` - Clear inference cache
- `GET /cache/stats` - Get cache statistics

## 🔧 Configuration

### Environment Variables
```bash
# Service Configuration
INFERENCE_SERVICE_PORT=55323
DATABASE_URL=sqlite:./data/inference.db
RUST_LOG=info

# Model Configuration
MODEL_CACHE_DIR=./models
MAX_LOADED_MODELS=5
MODEL_TIMEOUT_SECONDS=300

# Cache Configuration
CACHE_MAX_SIZE=1000
CACHE_TTL_HOURS=24
CACHE_CLEANUP_INTERVAL=3600

# Performance Tuning
MAX_CONCURRENT_INFERENCE=10
INFERENCE_TIMEOUT_MS=30000
MEMORY_LIMIT_MB=8192
```

### Model Registration
```json
{
  "name": "GPT-3.5-turbo",
  "description": "Large language model for text generation",
  "model_type": "TextGeneration",
  "framework": "transformers",
  "version": "1.0.0",
  "file_path": "/models/gpt-3.5-turbo.bin",
  "file_size": 1500000000,
  "tags": ["text", "generation", "chat"],
  "capabilities": ["TextGeneration", "Chat", "Translation"],
  "parameters": {
    "max_tokens": 4096,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

## 💬 Chat Interface Usage

### Starting a Chat Session
1. Select a model from the dropdown
2. Choose inference type (text, image, video, multimodal)
3. Adjust chat settings (temperature, max tokens, etc.)
4. Start typing to begin the conversation

### Supported Input Types
- **Text**: Direct text input for language models
- **Images**: Upload images for visual analysis
- **Videos**: Upload videos for temporal analysis
- **Multimodal**: Combine text with images/audio

### Chat Features
- **Real-time Responses**: WebSocket-based streaming
- **Typing Indicators**: Visual feedback during inference
- **Message History**: Persistent conversation storage
- **Model Switching**: Change models mid-conversation
- **Settings Persistence**: Remember user preferences

## 🎯 Use Cases

### Research & Development
- **Model Testing**: Compare different models on the same tasks
- **Performance Analysis**: Monitor inference metrics and optimization
- **Prototype Development**: Rapid prototyping with various models

### Production Applications
- **Customer Support**: AI-powered chat assistants
- **Content Analysis**: Automated image and video processing
- **Data Processing**: Batch inference for large datasets

### Educational
- **Model Education**: Learn about different AI models and capabilities
- **Interactive Learning**: Hands-on experience with AI inference
- **Research Projects**: Academic research with accessible AI tools

## 🔒 Security Features

- **Input Validation**: Sanitize all user inputs
- **Rate Limiting**: Prevent abuse with request throttling
- **Memory Management**: Automatic cleanup of unused models
- **Error Isolation**: Fail-safe error handling

## 📈 Performance Optimizations

- **Model Caching**: Keep frequently used models in memory
- **Result Caching**: Cache inference results for repeated queries
- **Batch Processing**: Efficient handling of multiple requests
- **Memory Pooling**: Reuse memory allocations for better performance

## 🛠️ Development

### Local Development
```bash
# Install dependencies
cargo build

# Run database migrations
sqlx migrate run

# Start the service
cargo run

# Run tests
cargo test
```

### Adding New Model Types
1. Implement the model wrapper in `inference.rs`
2. Add model type to `ModelType` enum
3. Update inference handlers
4. Add frontend support

### Custom Inference Logic
```rust
// Example: Custom text model
async fn infer_with_custom_model(&self, model: &CustomModel, request: &TextInferenceRequest) -> Result<String> {
    // Your custom inference logic here
    let result = model.generate(&request.prompt, &request.parameters).await?;
    Ok(result)
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Candle**: Rust-native ML framework
- **PyTorch**: Python ML framework integration
- **Transformers**: Hugging Face model ecosystem
- **Axum**: Modern Rust web framework

---

**Happy Inferencing! 🚀**
