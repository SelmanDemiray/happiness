-- Create models table
CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    model_type TEXT NOT NULL,
    framework TEXT NOT NULL,
    version TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    tags TEXT NOT NULL, -- JSON array
    capabilities TEXT NOT NULL, -- JSON array
    parameters TEXT NOT NULL, -- JSON object
    status TEXT NOT NULL,
    accuracy REAL,
    latency_ms INTEGER,
    memory_usage_mb INTEGER,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Create chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    model_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    status TEXT NOT NULL,
    settings TEXT NOT NULL, -- JSON object
    created_at DATETIME NOT NULL,
    last_activity DATETIME NOT NULL,
    message_count INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (model_id) REFERENCES models(id)
);

-- Create chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT NOT NULL, -- JSON object
    inference_time_ms INTEGER,
    token_count INTEGER,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- Create inference cache table
CREATE TABLE IF NOT EXISTS inference_cache (
    id TEXT PRIMARY KEY,
    cache_key TEXT NOT NULL UNIQUE,
    cache_type TEXT NOT NULL,
    data TEXT NOT NULL, -- JSON
    created_at DATETIME NOT NULL,
    expires_at DATETIME,
    access_count INTEGER NOT NULL DEFAULT 0,
    last_accessed DATETIME NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type);
CREATE INDEX IF NOT EXISTS idx_models_status ON models(status);
CREATE INDEX IF NOT EXISTS idx_models_created_at ON models(created_at);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_model_id ON chat_sessions(model_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

CREATE INDEX IF NOT EXISTS idx_inference_cache_key ON inference_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_inference_cache_type ON inference_cache(cache_type);
CREATE INDEX IF NOT EXISTS idx_inference_cache_expires_at ON inference_cache(expires_at);
