use axum::{
    extract::{Path, State, Multipart, Query, WebSocketUpgrade, ws::{WebSocket, Message}},
    http::{StatusCode, Method},
    response::{Json, IntoResponse},
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio::net::TcpListener;
use uuid::Uuid;
use tower_http::cors::{CorsLayer, Any};
use tower_http::trace::TraceLayer;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use chrono::{DateTime, Utc};
use anyhow::Result;

// ============================================================================
// SIMPLIFIED DATA STRUCTURES
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelInfo {
    pub id: String,
    pub name: String,
    pub description: String,
    pub model_type: String,
    pub status: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatSession {
    pub id: String,
    pub model_id: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatMessage {
    pub id: String,
    pub session_id: String,
    pub role: String,
    pub content: String,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
    pub timestamp: String,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
            timestamp: Utc::now().to_rfc3339(),
        }
    }

    pub fn error(error: String) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(error),
            timestamp: Utc::now().to_rfc3339(),
        }
    }
}

// ============================================================================
// APPLICATION STATE
// ============================================================================

#[derive(Clone)]
pub struct AppState {
    pub models: std::sync::Arc<tokio::sync::RwLock<Vec<ModelInfo>>>,
    pub sessions: std::sync::Arc<tokio::sync::RwLock<Vec<ChatSession>>>,
    pub messages: std::sync::Arc<tokio::sync::RwLock<Vec<ChatMessage>>>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            models: std::sync::Arc::new(tokio::sync::RwLock::new(Vec::new())),
            sessions: std::sync::Arc::new(tokio::sync::RwLock::new(Vec::new())),
            messages: std::sync::Arc::new(tokio::sync::RwLock::new(Vec::new())),
        }
    }
}

// ============================================================================
// MAIN APPLICATION
// ============================================================================

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "inference_service=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Initialize application state
    let app_state = AppState::new();

    // Models will be loaded from the backend service

    // Build the application
    let app = Router::new()
        // Model management routes
        .route("/models", get(list_models))
        .route("/models/:id", get(get_model))
        
        // Inference routes
        .route("/inference/text", post(infer_text))
        .route("/inference/image", post(infer_image))
        
        // Chat routes
        .route("/chat/start", post(start_chat))
        .route("/chat/:session_id/message", post(send_message))
        .route("/chat/:session_id/history", get(get_chat_history))
        
        // Health check
        .route("/health", get(health_check))
        .with_state(app_state)
        .layer(
            CorsLayer::new()
                .allow_origin(Any)
                .allow_methods([Method::GET, Method::POST])
                .allow_headers(Any),
        )
        .layer(TraceLayer::new_for_http());

    let port = std::env::var("INFERENCE_SERVICE_PORT")
        .unwrap_or_else(|_| "55323".to_string())
        .parse::<u16>()?;

    let listener = TcpListener::bind(format!("0.0.0.0:{}", port)).await?;
    tracing::info!("🚀 Inference Service running on port {}", port);
    
    axum::serve(listener, app).await?;
    
    Ok(())
}

// ============================================================================
// MODEL HANDLERS
// ============================================================================

async fn list_models(State(state): State<AppState>) -> Result<Json<ApiResponse<Vec<ModelInfo>>>, StatusCode> {
    // Fetch models from backend service
    let backend_url = std::env::var("BACKEND_URL").unwrap_or_else(|_| "http://localhost:55320".to_string());
    
    match reqwest::get(&format!("{}/models", backend_url)).await {
        Ok(response) => {
            if response.status().is_success() {
                match response.json::<serde_json::Value>().await {
                    Ok(json_response) => {
                        if let Some(data) = json_response.get("data") {
                            if let Some(models_data) = data.get("models") {
                                if let Ok(backend_models) = serde_json::from_value::<Vec<serde_json::Value>>(models_data.clone()) {
                                    // Convert backend models to inference service format
                                    let models: Vec<ModelInfo> = backend_models.into_iter().filter_map(|model_json| {
                                        if let (Some(id), Some(name)) = (
                                            model_json.get("id").and_then(|v| v.as_str()),
                                            model_json.get("name").and_then(|v| v.as_str())
                                        ) {
                                            Some(ModelInfo {
                                                id: id.to_string(),
                                                name: name.to_string(),
                                                description: model_json.get("description").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                                                model_type: model_json.get("input_type").and_then(|v| v.as_str()).unwrap_or("unknown").to_string(),
                                                status: "available".to_string(),
                                                created_at: model_json.get("created_at").and_then(|v| v.as_str())
                                                    .and_then(|s| chrono::DateTime::parse_from_rfc3339(s).ok())
                                                    .map(|dt| dt.with_timezone(&Utc))
                                                    .unwrap_or_else(Utc::now),
                                            })
                                        } else {
                                            None
                                        }
                                    }).collect();
                                    
                                    tracing::info!("Fetched {} models from backend", models.len());
                                    return Ok(Json(ApiResponse::success(models)));
                                }
                            }
                        }
                    }
                    Err(e) => {
                        tracing::error!("Failed to parse backend response: {}", e);
                    }
                }
            } else {
                tracing::error!("Backend returned error status: {}", response.status());
            }
        }
        Err(e) => {
            tracing::error!("Failed to fetch models from backend: {}", e);
        }
    }
    
    // Fallback to empty list if backend is unavailable
    Ok(Json(ApiResponse::success(Vec::new())))
}

async fn get_model(State(state): State<AppState>, Path(id): Path<String>) -> Result<Json<ApiResponse<ModelInfo>>, StatusCode> {
    let models = state.models.read().await;
    if let Some(model) = models.iter().find(|m| m.id == id) {
        Ok(Json(ApiResponse::success(model.clone())))
    } else {
        Err(StatusCode::NOT_FOUND)
    }
}

// ============================================================================
// INFERENCE HANDLERS
// ============================================================================

#[derive(Debug, Serialize, Deserialize)]
pub struct TextInferenceRequest {
    pub model_id: String,
    pub prompt: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TextInferenceResponse {
    pub generated_text: String,
    pub inference_time_ms: u64,
}

async fn infer_text(
    State(state): State<AppState>,
    Json(request): Json<TextInferenceRequest>,
) -> Result<Json<ApiResponse<TextInferenceResponse>>, StatusCode> {
    // Simulate inference
    let response = TextInferenceResponse {
        generated_text: format!("AI Response to: {}", request.prompt),
        inference_time_ms: 100,
    };
    
    Ok(Json(ApiResponse::success(response)))
}

async fn infer_image(
    State(state): State<AppState>,
    mut multipart: Multipart,
) -> Result<Json<ApiResponse<serde_json::Value>>, StatusCode> {
    // Simulate image inference
    let response = serde_json::json!({
        "predictions": [
            {
                "label": "cat",
                "confidence": 0.95
            }
        ],
        "inference_time_ms": 200
    });
    
    Ok(Json(ApiResponse::success(response)))
}

// ============================================================================
// CHAT HANDLERS
// ============================================================================

#[derive(Debug, Serialize, Deserialize)]
pub struct StartChatRequest {
    pub model_id: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SendMessageRequest {
    pub content: String,
}

async fn start_chat(
    State(state): State<AppState>,
    Json(request): Json<StartChatRequest>,
) -> Result<Json<ApiResponse<ChatSession>>, StatusCode> {
    let session = ChatSession {
        id: Uuid::new_v4().to_string(),
        model_id: request.model_id,
        created_at: Utc::now(),
    };

    {
        let mut sessions = state.sessions.write().await;
        sessions.push(session.clone());
    }

    Ok(Json(ApiResponse::success(session)))
}

async fn send_message(
    State(state): State<AppState>,
    Path(session_id): Path<String>,
    Json(request): Json<SendMessageRequest>,
) -> Result<Json<ApiResponse<ChatMessage>>, StatusCode> {
    // Create user message
    let user_message = ChatMessage {
        id: Uuid::new_v4().to_string(),
        session_id: session_id.clone(),
        role: "user".to_string(),
        content: request.content.clone(),
        timestamp: Utc::now(),
    };

    {
        let mut messages = state.messages.write().await;
        messages.push(user_message);
    }

    // Create AI response
    let ai_message = ChatMessage {
        id: Uuid::new_v4().to_string(),
        session_id: session_id.clone(),
        role: "assistant".to_string(),
        content: format!("AI Response to: {}", request.content),
        timestamp: Utc::now(),
    };

    {
        let mut messages = state.messages.write().await;
        messages.push(ai_message.clone());
    }

    Ok(Json(ApiResponse::success(ai_message)))
}

async fn get_chat_history(
    State(state): State<AppState>,
    Path(session_id): Path<String>,
) -> Result<Json<ApiResponse<Vec<ChatMessage>>>, StatusCode> {
    let messages = state.messages.read().await;
    let session_messages: Vec<ChatMessage> = messages
        .iter()
        .filter(|m| m.session_id == session_id)
        .cloned()
        .collect();

    Ok(Json(ApiResponse::success(session_messages)))
}

// ============================================================================
// UTILITY HANDLERS
// ============================================================================

async fn health_check() -> Json<ApiResponse<HashMap<String, String>>> {
    let mut health = HashMap::new();
    health.insert("status".to_string(), "healthy".to_string());
    health.insert("timestamp".to_string(), Utc::now().to_rfc3339());
    Json(ApiResponse::success(health))
}