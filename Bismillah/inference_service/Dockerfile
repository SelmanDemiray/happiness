FROM rust:latest as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for ML models (optional)
# RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# RUN pip3 install transformers tokenizers datasets accelerate

# Set working directory
WORKDIR /app

# Copy Cargo files
COPY Cargo.toml ./

# Copy source code
COPY src ./src
COPY migrations ./migrations

# Build the application
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libssl3 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python ML dependencies (optional)
# RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# RUN pip3 install transformers tokenizers datasets accelerate

# Create app user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy the binary from builder stage
COPY --from=builder /app/target/release/inference_service /app/inference_service

# Copy migrations
COPY --from=builder /app/migrations ./migrations

# Create directories for cache and models
RUN mkdir -p /app/cache /app/models /app/data
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Expose port
EXPOSE 55323

# Set environment variables
ENV RUST_LOG=info
ENV DATABASE_URL=sqlite:/app/data/inference.db
ENV INFERENCE_SERVICE_PORT=55323

# Run the application
CMD ["./inference_service"]
