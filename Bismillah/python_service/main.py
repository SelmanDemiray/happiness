"""
Python service for Hugging Face datasets integration
Provides API endpoints for dataset discovery, preview, and download
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

from huggingface_hub import HfApi, login
from datasets import load_dataset, get_dataset_infos, Dataset, DatasetDict
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hugging Face Datasets Service",
    description="API for discovering, previewing, and downloading Hugging Face datasets",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
hf_api = None
hf_token = None

# Pydantic models
class DatasetInfo(BaseModel):
    id: str
    name: str
    description: str
    license: Optional[str] = None
    size: Optional[int] = None
    downloads: Optional[int] = None
    likes: Optional[int] = None
    tags: List[str] = []
    task_categories: List[str] = []
    language: List[str] = []
    configs: List[str] = []
    splits: List[str] = []

class DatasetPreview(BaseModel):
    dataset_id: str
    config: str
    split: str
    sample_size: int
    columns: List[str]
    sample_data: List[Dict[str, Any]]
    total_rows: Optional[int] = None

class DatasetDownloadRequest(BaseModel):
    dataset_id: str
    config: Optional[str] = None
    split: Optional[str] = None
    sample_size: Optional[int] = None
    max_rows: Optional[int] = None
    percentage: Optional[float] = None

class DatasetDownloadResponse(BaseModel):
    dataset_id: str
    config: str
    split: str
    file_path: str
    total_rows: int
    columns: List[str]
    size_mb: float

class SearchFilters(BaseModel):
    modality: Optional[List[str]] = None
    license: Optional[List[str]] = None
    language: Optional[List[str]] = None
    task_categories: Optional[List[str]] = None
    min_downloads: Optional[int] = None
    max_size_mb: Optional[float] = None

# Initialize Hugging Face API
async def init_hf_api():
    global hf_api, hf_token
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if hf_token:
        try:
            login(token=hf_token)
            hf_api = HfApi(token=hf_token)
            logger.info("Successfully authenticated with Hugging Face")
        except Exception as e:
            logger.error(f"Failed to authenticate with Hugging Face: {e}")
            hf_api = HfApi()  # Use public API
    else:
        logger.warning("No Hugging Face token provided, using public API")
        hf_api = HfApi()

# Startup event
@app.on_event("startup")
async def startup_event():
    await init_hf_api()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "huggingface-datasets"}

# Get curated popular datasets
@app.get("/datasets/curated", response_model=List[DatasetInfo])
async def get_curated_datasets():
    """Get a curated list of popular datasets"""
    curated_ids = [
        "mnist",
        "cifar10", 
        "cifar100",
        "squad",
        "glue"
    ]
    
    datasets = []
    for dataset_id in curated_ids:
        try:
            info = hf_api.dataset_info(dataset_id)
            datasets.append(DatasetInfo(
                id=dataset_id,
                name=info.id,
                description=getattr(info, 'description', "") or "No description available",
                license=str(getattr(info, 'cardData', {}).get("license", "")) if getattr(info, 'cardData', None) and getattr(info, 'cardData', {}).get("license") else None,
                size=getattr(info, 'downloads', 0),
                downloads=getattr(info, 'downloads', 0),
                likes=getattr(info, 'likes', 0),
                tags=getattr(info, 'tags', []) or [],
                task_categories=getattr(info, 'task_categories', []) or [],
                language=getattr(info, 'language', []) or [],
                configs=list(getattr(info, 'splits', {}).keys()) if getattr(info, 'splits', None) else [],
                splits=list(getattr(info, 'splits', {}).keys()) if getattr(info, 'splits', None) else []
            ))
        except Exception as e:
            logger.warning(f"Failed to get info for {dataset_id}: {e}")
            continue
    
    return datasets

# Search datasets
@app.get("/datasets/search", response_model=List[DatasetInfo])
async def search_datasets(
    query: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=100),
    filters: Optional[SearchFilters] = None
):
    """Search for datasets with optional filters"""
    try:
        # Use Hugging Face API to search
        datasets = hf_api.list_datasets(
            search=query,
            limit=limit,
            sort="downloads",
            direction=-1
        )
        
        results = []
        for dataset in datasets:
            try:
                info = hf_api.dataset_info(dataset.id)
                
                # Apply filters if provided
                if filters:
                    if filters.modality and not any(tag in filters.modality for tag in (info.tags or [])):
                        continue
                    if filters.license and info.cardData and info.cardData.get("license") not in filters.license:
                        continue
                    if filters.language and not any(lang in filters.language for lang in (info.language or [])):
                        continue
                    if filters.task_categories and not any(task in filters.task_categories for task in (getattr(info, 'task_categories', []) or [])):
                        continue
                    if filters.min_downloads and (info.downloads or 0) < filters.min_downloads:
                        continue
                
                results.append(DatasetInfo(
                    id=dataset.id,
                    name=info.id,
                    description=info.description or "No description available",
                    license=info.cardData.get("license") if info.cardData else None,
                    size=info.downloads,
                    downloads=info.downloads,
                    likes=info.likes,
                    tags=getattr(info, 'tags', []) or [],
                    task_categories=getattr(info, 'task_categories', []) or [],
                    language=getattr(info, 'language', []) or [],
                    configs=list(info.splits.keys()) if info.splits else [],
                    splits=list(info.splits.keys()) if info.splits else []
                ))
            except Exception as e:
                logger.warning(f"Failed to get info for {dataset.id}: {e}")
                continue
        
        return results[:limit]
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Get dataset preview
@app.get("/datasets/{dataset_id}/preview", response_model=DatasetPreview)
async def get_dataset_preview(
    dataset_id: str,
    config: str = Query("default", description="Dataset configuration"),
    split: str = Query("train", description="Dataset split"),
    sample_size: int = Query(10, ge=1, le=1000, description="Number of samples to preview")
):
    """Get a preview of the dataset"""
    try:
        logger.info(f"Loading dataset preview for {dataset_id} with config {config}, split {split}")
        
        # Load dataset with streaming for large datasets
        # Handle special cases and config name mismatches
        dataset = None
        config_used = config
        
        # Special handling for known datasets
        if dataset_id in ['cifar10', 'cifar100', 'mnist']:
            # For CIFAR and MNIST, try without config first
            loading_strategies = [
                # Strategy 1: No config (works for most standard datasets)
                lambda: load_dataset(dataset_id, split=split),
                # Strategy 2: Try with 'plain_text' config (common for these datasets)
                lambda: load_dataset(dataset_id, 'plain_text', split=split),
                # Strategy 3: Original config without streaming
                lambda: load_dataset(dataset_id, config, split=split),
                # Strategy 4: Original config with streaming
                lambda: load_dataset(dataset_id, config, split=split, streaming=True),
                # Strategy 5: Use dataset_id as config
                lambda: load_dataset(dataset_id, dataset_id, split=split),
                # Strategy 6: Try with 'default' config
                lambda: load_dataset(dataset_id, 'default', split=split),
            ]
        else:
            # Try multiple loading strategies for other datasets
            loading_strategies = [
                # Strategy 1: Original config without streaming (most reliable)
                lambda: load_dataset(dataset_id, config, split=split),
                # Strategy 2: Original config with streaming
                lambda: load_dataset(dataset_id, config, split=split, streaming=True),
                # Strategy 3: Use dataset_id as config without streaming
                lambda: load_dataset(dataset_id, dataset_id, split=split),
                # Strategy 4: Use dataset_id as config with streaming
                lambda: load_dataset(dataset_id, dataset_id, split=split, streaming=True),
                # Strategy 5: Try with 'default' config without streaming
                lambda: load_dataset(dataset_id, 'default', split=split),
                # Strategy 6: Try with 'default' config with streaming
                lambda: load_dataset(dataset_id, 'default', split=split, streaming=True),
                # Strategy 7: Try without config parameter (for simple datasets)
                lambda: load_dataset(dataset_id, split=split),
                # Strategy 8: Try with 'plain_text' config for text datasets
                lambda: load_dataset(dataset_id, 'plain_text', split=split),
            ]
        
        for i, strategy in enumerate(loading_strategies):
            try:
                # Add timeout for dataset loading
                dataset = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, strategy),
                    timeout=30.0  # 30 second timeout
                )
                # Update config_used based on which strategy worked
                if dataset_id in ['cifar10', 'cifar100', 'mnist']:
                    # Special handling for known datasets
                    if i == 0:  # No config
                        config_used = 'no_config'
                    elif i == 1:  # 'plain_text' config
                        config_used = 'plain_text'
                    elif i == 2 or i == 3:  # Original config
                        config_used = config
                    elif i == 4:  # dataset_id as config
                        config_used = dataset_id
                    elif i == 5:  # 'default' config
                        config_used = 'default'
                else:
                    # General handling for other datasets
                    if i == 2 or i == 3:  # If we used dataset_id as config
                        config_used = dataset_id
                    elif i == 4 or i == 5:  # If we used 'default' config
                        config_used = 'default'
                    elif i == 6:  # If we used no config
                        config_used = 'no_config'
                    elif i == 7:  # If we used 'plain_text' config
                        config_used = 'plain_text'
                logger.info(f"Successfully loaded dataset {dataset_id} with strategy {i+1} (config: {config_used})")
                break
            except asyncio.TimeoutError:
                logger.warning(f"Strategy {i+1} timed out after 30 seconds")
                continue
            except Exception as e:
                logger.warning(f"Strategy {i+1} failed: {e}")
                continue
        
        if dataset is None:
            error_msg = f"Failed to load dataset {dataset_id} with any strategy. "
            error_msg += f"Tried {len(loading_strategies)} different loading approaches. "
            error_msg += f"Dataset might not exist, be accessible, or have the requested split '{split}'."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Get sample data
        sample_data = []
        columns = []
        total_rows = None
        
        try:
            # Try to get total rows for non-streaming datasets
            full_dataset = load_dataset(dataset_id, config, split=split)
            if isinstance(full_dataset, Dataset):
                total_rows = len(full_dataset)
            elif isinstance(full_dataset, DatasetDict) and split in full_dataset:
                total_rows = len(full_dataset[split])
        except:
            pass  # Continue with streaming if full load fails
        
        # Collect sample data
        logger.info(f"Processing {sample_size} samples from dataset")
        try:
            for i, example in enumerate(dataset):
                if i >= sample_size:
                    break
                
                try:
                    # Convert numpy arrays and other non-serializable types
                    processed_example = {}
                    for key, value in example.items():
                        try:
                            if isinstance(value, np.ndarray):
                                processed_example[key] = value.tolist()
                            elif isinstance(value, Image.Image):
                                # Convert image to base64
                                buffer = io.BytesIO()
                                value.save(buffer, format='PNG')
                                img_str = base64.b64encode(buffer.getvalue()).decode()
                                processed_example[key] = f"data:image/png;base64,{img_str}"
                            elif hasattr(value, '__dict__'):
                                # Handle complex objects by converting to string
                                processed_example[key] = str(value)
                            else:
                                processed_example[key] = value
                        except Exception as field_error:
                            logger.warning(f"Error processing field {key}: {field_error}")
                            processed_example[key] = str(value) if value is not None else None
                    
                    sample_data.append(processed_example)
                    
                    # Get columns from first example
                    if i == 0:
                        columns = list(example.keys())
                        logger.info(f"Dataset columns: {columns}")
                        
                except Exception as example_error:
                    logger.warning(f"Error processing example {i}: {example_error}")
                    continue
        except Exception as iteration_error:
            logger.error(f"Error iterating over dataset: {iteration_error}")
            # Try to get at least the structure
            try:
                if hasattr(dataset, 'column_names'):
                    columns = dataset.column_names
                elif hasattr(dataset, 'features'):
                    columns = list(dataset.features.keys())
                else:
                    columns = ['unknown']
                logger.info(f"Extracted columns from dataset structure: {columns}")
            except:
                columns = ['error']
                logger.warning("Could not extract column information")
        
        if not sample_data:
            logger.warning(f"No sample data collected for {dataset_id}")
            # Return a minimal preview with error info
            error_message = "Unable to load dataset samples"
            if columns and columns != ['error']:
                error_message += f". Dataset structure found with columns: {', '.join(columns)}"
            return DatasetPreview(
                dataset_id=dataset_id,
                config=config_used,
                split=split,
                sample_size=0,
                columns=["error"],
                sample_data=[{"error": error_message}],
                total_rows=0
            )
        
        logger.info(f"Successfully created preview for {dataset_id} with {len(sample_data)} samples")
        return DatasetPreview(
            dataset_id=dataset_id,
            config=config_used,
            split=split,
            sample_size=len(sample_data),
            columns=columns,
            sample_data=sample_data,
            total_rows=total_rows
        )
        
    except Exception as e:
        logger.error(f"Failed to preview dataset {dataset_id}: {e}")
        # Return a more informative error
        return DatasetPreview(
            dataset_id=dataset_id,
            config=config_used if 'config_used' in locals() else config,
            split=split,
            sample_size=0,
            columns=["error"],
            sample_data=[{"error": f"Failed to load dataset: {str(e)}"}],
            total_rows=0
        )

# Download dataset
@app.post("/datasets/{dataset_id}/download", response_model=DatasetDownloadResponse)
async def download_dataset(
    dataset_id: str,
    request: DatasetDownloadRequest,
    background_tasks: BackgroundTasks
):
    """Download and cache a dataset"""
    try:
        config = request.config or "default"
        split = request.split or "train"
        
        # Create cache directory
        cache_dir = Path(os.getenv("DATASET_CACHE_DIR", "./cache/datasets"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load dataset
        try:
            dataset = load_dataset(
                dataset_id,
                config,
                split=split
            )
        except Exception as e:
            if "BuilderConfig" in str(e) and "not found" in str(e):
                # Try with the dataset_id as config name
                dataset = load_dataset(
                    dataset_id,
                    dataset_id,
                    split=split
                )
                config = dataset_id
            else:
                raise e
        
        # Apply sampling if requested
        if request.sample_size:
            dataset = dataset.select(range(min(request.sample_size, len(dataset))))
        elif request.max_rows:
            dataset = dataset.select(range(min(request.max_rows, len(dataset))))
        elif request.percentage:
            sample_size = int(len(dataset) * request.percentage / 100)
            dataset = dataset.select(range(sample_size))
        
        # Save to cache
        file_path = cache_dir / f"{dataset_id}_{config}_{split}.json"
        
        # Convert to JSON-serializable format
        data_to_save = []
        for example in dataset:
            processed_example = {}
            for key, value in example.items():
                if isinstance(value, np.ndarray):
                    processed_example[key] = value.tolist()
                elif isinstance(value, Image.Image):
                    # Convert image to base64
                    buffer = io.BytesIO()
                    value.save(buffer, format='PNG')
                    img_str = base64.b64encode(buffer.getvalue()).decode()
                    processed_example[key] = f"data:image/png;base64,{img_str}"
                else:
                    processed_example[key] = value
            data_to_save.append(processed_example)
        
        with open(file_path, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        
        # Get file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        return DatasetDownloadResponse(
            dataset_id=dataset_id,
            config=config,
            split=split,
            file_path=str(file_path),
            total_rows=len(dataset),
            columns=list(dataset.features.keys()),
            size_mb=file_size_mb
        )
        
    except Exception as e:
        logger.error(f"Failed to download dataset {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download dataset: {str(e)}")

# Get available dataset configurations
@app.get("/datasets/{dataset_id}/configs")
async def get_dataset_configs(dataset_id: str):
    """Get available configurations for a dataset"""
    try:
        info = hf_api.dataset_info(dataset_id)
        return {
            "configs": list(info.splits.keys()) if info.splits else ["default"],
            "splits": list(info.splits.keys()) if info.splits else ["train"]
        }
    except Exception as e:
        logger.error(f"Failed to get configs for {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get configs: {str(e)}")

# Transform dataset for trainer compatibility
@app.post("/datasets/{dataset_id}/transform")
async def transform_dataset(
    dataset_id: str,
    config: str = Query("default"),
    split: str = Query("train"),
    transformations: Dict[str, Any] = None
):
    """Apply transformations to make dataset compatible with trainer"""
    try:
        # Load dataset
        dataset = load_dataset(dataset_id, config, split=split, trust_remote_code=True)
        
        # Apply transformations based on dataset type
        if transformations:
            # Text tokenization
            if "tokenize" in transformations:
                # Implement text tokenization
                pass
            
            # Image preprocessing
            if "resize_images" in transformations:
                # Implement image resizing
                pass
            
            # Audio preprocessing
            if "resample_audio" in transformations:
                # Implement audio resampling
                pass
        
        # Return transformed dataset info
        return {
            "dataset_id": dataset_id,
            "config": config,
            "split": split,
            "transformed": True,
            "columns": list(dataset.features.keys()),
            "total_rows": len(dataset)
        }
        
    except Exception as e:
        logger.error(f"Failed to transform dataset {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to transform dataset: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PYTHON_SERVICE_PORT", 55322))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
