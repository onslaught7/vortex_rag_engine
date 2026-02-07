# 1. Base Image
FROM python:3.12-slim

# 2. Install uv (The "Senior" Move: Copy binary directly)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 3. Copy dependencies
COPY requirements.txt .

# 4. Install with uv
# --system: Install into system python (no venv needed inside container)
# --no-cache: Keep image small
RUN uv pip install --system --no-cache -r requirements.txt

# 5. Copy Application Code
COPY worker.py .

# 6. Runtime Config
ENV PYTHONUNBUFFERED=1

CMD ["python", "worker.py"]