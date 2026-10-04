# Stage 1: The Builder
# This stage installs all dependencies, including those needed for specific deployments.
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy pinned runtime dependencies first to leverage Docker layer caching.
COPY code_review_assistant/requirements.txt ./requirements.txt

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# ---
# Stage 2: The Final Production Image
# This stage creates a lean, secure image using the artifacts from the builder.
FROM python:3.11-slim

WORKDIR /app

# Copy executable binaries (uvicorn, adk, poetry, etc.) from builder
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code from the builder stage
COPY --from=builder /app /app

# Create a dedicated, non-root user for security best practices
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables. These can be overridden at runtime by Cloud Run or Docker.
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
# This provides a fallback for manual 'docker run' commands, but our deploy.sh script
# will always provide the correct URI for the target environment.
ENV SESSION_SERVICE_URI="sqlite:///./sessions.db"

# Start the FastAPI app, honoring Render's injected PORT when present.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
