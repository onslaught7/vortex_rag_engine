# 1. Base Image: Python 3.12 (Slim & Stable)
FROM python:3.12-slim

# 2. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# 3. Copy the definition files first (for Docker layer caching)
COPY pyproject.toml uv.lock ./

# 4. Install dependencies
# --frozen: Ensures we use exactly what is in uv.lock
# --no-dev: Skip test/dev dependencies
RUN uv sync --frozen --no-dev

# 5. Copy your application logic
COPY worker.py .

# 6. Set Environment
# IMPORTANT: Point to the virtual environment uv created
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# 7. Run
CMD ["python", "worker.py"]