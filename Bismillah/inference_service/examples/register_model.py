#!/usr/bin/env python3
"""
Example script to register models with the inference service.
This demonstrates how to add models to the model registry.
"""

import requests
import json
import os
from pathlib import Path

# Configuration
INFERENCE_SERVICE_URL = "http://localhost:55323"
MODELS_DIR = "./models"

def register_text_model():
    """Register a text generation model."""
    model_data = {
        "name": "GPT-2 Small",
        "description": "Small GPT-2 model for text generation",
        "model_type": "TextGeneration",
        "framework": "transformers",
        "version": "1.0.0",
        "file_path": f"{MODELS_DIR}/gpt2-small.bin",
        "file_size": 500000000,  # 500MB
        "tags": ["text", "generation", "gpt2"],
        "capabilities": ["TextGeneration", "Chat", "Completion"],
        "parameters": {
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }
    
    response = requests.post(f"{INFERENCE_SERVICE_URL}/models", json=model_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Registered text model: {result['data']['id']}")
        return result['data']['id']
    else:
        print(f"❌ Failed to register text model: {response.text}")
        return None

def register_image_model():
    """Register an image classification model."""
    model_data = {
        "name": "ResNet-50",
        "description": "ResNet-50 model for image classification",
        "model_type": "ImageClassification",
        "framework": "torch",
        "version": "1.0.0",
        "file_path": f"{MODELS_DIR}/resnet50.pth",
        "file_size": 100000000,  # 100MB
        "tags": ["image", "classification", "resnet"],
        "capabilities": ["ImageClassification", "FeatureExtraction"],
        "parameters": {
            "num_classes": 1000,
            "input_size": [224, 224],
            "pretrained": True
        }
    }
    
    response = requests.post(f"{INFERENCE_SERVICE_URL}/models", json=model_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Registered image model: {result['data']['id']}")
        return result['data']['id']
    else:
        print(f"❌ Failed to register image model: {response.text}")
        return None

def register_video_model():
    """Register a video analysis model."""
    model_data = {
        "name": "Video Transformer",
        "description": "Transformer model for video understanding",
        "model_type": "VideoAnalysis",
        "framework": "transformers",
        "version": "1.0.0",
        "file_path": f"{MODELS_DIR}/video-transformer.bin",
        "file_size": 2000000000,  # 2GB
        "tags": ["video", "analysis", "transformer"],
        "capabilities": ["VideoAnalysis", "ObjectTracking", "SceneUnderstanding"],
        "parameters": {
            "max_frames": 32,
            "frame_size": [224, 224],
            "temporal_stride": 4
        }
    }
    
    response = requests.post(f"{INFERENCE_SERVICE_URL}/models", json=model_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Registered video model: {result['data']['id']}")
        return result['data']['id']
    else:
        print(f"❌ Failed to register video model: {response.text}")
        return None

def register_multimodal_model():
    """Register a multimodal model."""
    model_data = {
        "name": "CLIP",
        "description": "CLIP model for multimodal understanding",
        "model_type": "Multimodal",
        "framework": "transformers",
        "version": "1.0.0",
        "file_path": f"{MODELS_DIR}/clip.bin",
        "file_size": 1500000000,  # 1.5GB
        "tags": ["multimodal", "vision", "language", "clip"],
        "capabilities": ["Multimodal", "ImageClassification", "TextEmbedding"],
        "parameters": {
            "max_text_length": 77,
            "image_size": [224, 224],
            "embedding_dim": 512
        }
    }
    
    response = requests.post(f"{INFERENCE_SERVICE_URL}/models", json=model_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Registered multimodal model: {result['data']['id']}")
        return result['data']['id']
    else:
        print(f"❌ Failed to register multimodal model: {response.text}")
        return None

def list_models():
    """List all registered models."""
    response = requests.get(f"{INFERENCE_SERVICE_URL}/models")
    if response.status_code == 200:
        result = response.json()
        print(f"\n📋 Registered Models ({len(result['data'])}):")
        for model in result['data']:
            print(f"  • {model['name']} ({model['model_type']}) - {model['status']}")
    else:
        print(f"❌ Failed to list models: {response.text}")

def test_inference():
    """Test inference with a registered model."""
    # First, get available models
    response = requests.get(f"{INFERENCE_SERVICE_URL}/models")
    if response.status_code != 200:
        print("❌ No models available for testing")
        return
    
    models = response.json()['data']
    if not models:
        print("❌ No models registered")
        return
    
    # Test text inference
    text_models = [m for m in models if m['model_type'] == 'TextGeneration']
    if text_models:
        model_id = text_models[0]['id']
        print(f"\n🧪 Testing text inference with {text_models[0]['name']}...")
        
        inference_data = {
            "model_id": model_id,
            "prompt": "Hello, how are you?",
            "parameters": {
                "max_tokens": 50,
                "temperature": 0.7
            }
        }
        
        response = requests.post(f"{INFERENCE_SERVICE_URL}/inference/text", json=inference_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Inference successful: {result['data']['generated_text']}")
        else:
            print(f"❌ Inference failed: {response.text}")

def main():
    """Main function to register example models."""
    print("🚀 Registering example models with inference service...")
    
    # Create models directory if it doesn't exist
    Path(MODELS_DIR).mkdir(exist_ok=True)
    
    # Register different types of models
    text_model_id = register_text_model()
    image_model_id = register_image_model()
    video_model_id = register_video_model()
    multimodal_model_id = register_multimodal_model()
    
    # List all models
    list_models()
    
    # Test inference
    test_inference()
    
    print("\n✨ Model registration complete!")
    print("You can now use these models in the chat interface at http://localhost:55321")

if __name__ == "__main__":
    main()
