# Multi-stage build for lightweight production image
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install system dependencies for building
RUN apk add --no-cache gcc musl-dev jpeg-dev zlib-dev

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv

# Install dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.11-alpine

WORKDIR /app

# Install runtime dependencies only
RUN apk add --no-cache jpeg zlib

# Copy Python environment and application
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY templates/ ./templates/

# Create directories for uploads and ensure permissions
RUN mkdir -p uploads static && \
    adduser -D -s /bin/sh appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Activate virtual environment and set PYTHONPATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

EXPOSE 8001

CMD ["uvicorn", "src.photo_annotator.main:app", "--host", "0.0.0.0", "--port", "8001"]