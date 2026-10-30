# Multi-stage production Dockerfile for AI Meeting-to-Action Agent
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml setup.py ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir build

COPY src ./src
RUN pip install --no-cache-dir .

# Final stage: minimal runtime image
FROM python:3.11-slim AS runtime

WORKDIR /app

# Security: create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1001 appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /build/src /app/src
COPY samples /app/samples
COPY web /app/web

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    API_PORT=8000

USER appuser

EXPOSE 8000 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "meeting_action_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
