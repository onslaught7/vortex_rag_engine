# Vortex RAG Engine: High-Throughput Asynchronous Ingestion

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Go](https://img.shields.io/badge/Gateway-Go_1.21-00ADD8.svg)
![Python](https://img.shields.io/badge/Worker-Python_3.12-3776AB.svg)
![Redis](https://img.shields.io/badge/Broker-Redis-DC382D.svg)

> **The Problem:** Standard RAG applications are synchronous. If a user uploads 50 documents, the web server hangs while waiting for embeddings, leading to timeouts and crashes under load.
> 
> **The Solution:** Vortex is a decoupled ingestion engine. It uses **Go** for high-concurrency request handling and **Python** for background AI processing, linked by a **Redis** buffer.

---

## 🏗 Architecture

The system is designed to handle **burst traffic** without dropping requests.

```mermaid
graph LR
    Client[Client / Frontend] -->|POST /ingest (JSON)| Gateway
    subgraph "High-Speed Ingestion Layer"
        Gateway[Go API Gateway (Fiber)]
    end
    Gateway -->|LPUSH (Instant)| Redis[Redis Queue]
    subgraph "Async Processing Layer"
        Redis -->|BRPOP (Blocking)| Worker[Python AI Worker]
        Worker -->|Generate Embeddings| OpenAI
        Worker -->|Upsert Vectors| VectorDB[(Vector Store)]
    end

```

### Core Components

| Service | Tech Stack | Role | Why this tech? |
| --- | --- | --- | --- |
| **The Gateway** | **Go (Fiber)** | Ingestion | Handles 10k+ concurrent requests/sec with minimal RAM. Accepts data and returns `202 Accepted` instantly. |
| **The Broker** | **Redis** | Message Queue | Acts as a "Shock Absorber" for traffic spikes. Holds tasks until the worker is ready. |
| **The Worker** | **Python 3.12** | Processing | Leveraging the rich AI ecosystem (LangChain/OpenAI) to handle complex vectorization logic in the background. |

---

## 🚀 Key Features

* **Non-Blocking I/O:** The Go Gateway never waits for OpenAI. It acknowledges receipt and offloads the work.
* **Backpressure Handling:** Redis acts as a buffer. If the AI API is slow, the Queue grows, but the Gateway keeps accepting new traffic.
* **Polyglot Architecture:** Demonstrates the "Right Tool for the Job" philosophy—Go for speed, Python for Logic.
* **Dockerized:** Entire stack spins up with a single compose command.

---

## 🛠️ Getting Started

### Prerequisites

* Docker & Docker Compose
* OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone [https://github.com/onslaught7/vortex_rag_engine.git](https://github.com/onslaught7/vortex_rag_engine.git)
cd vortex-rag-engine

```


2. **Set Environment Variables**
Create a `.env` file in the root:
```env
OPENAI_API_KEY=sk-your-key-here
REDIS_HOST=redis
REDIS_PORT=6379

```


3. **Launch the System**
```bash
docker-compose up --build

```



---

## ⚡ Usage

### 1. Ingest a Document

Send a request to the Go Gateway. It will respond instantly.

```bash
curl -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "u-123",
    "document_id": "doc-001",
    "content": "Golang is excellent for high-throughput systems due to goroutines."
  }'

```

**Response:**

```json
{
  "status": "accepted",
  "task_id": "job-550e8400-e29b",
  "queue_depth": 1
}

```

### 2. Check the Worker Logs

You will see the Python worker pick up the task asynchronously:

```text
[Worker] Processing task job-550e8400-e29b...
[Worker] Embedding generated (1536 dims).
[Worker] Saved to Vector Store. Time taken: 0.4s

```

---

## 🧠 Engineering Decisions

**Why not just use Python for everything?**
Python's `asyncio` is great, but under heavy CPU load (like JSON validation at scale), the GIL (Global Interpreter Lock) becomes a bottleneck. Go's goroutines allow us to handle thousands of concurrent connections with a tiny memory footprint.

**Why Redis instead of Kafka?**
For this scale, Redis List (`LPUSH`/`BRPOP`) provides the perfect balance of simplicity and performance (<1ms latency). Kafka would introduce unnecessary operational complexity for a simple job queue.

---

## 📜 License

MIT

```

---