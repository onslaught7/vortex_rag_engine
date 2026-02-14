# MarketPulse Engine: High-Throughput Financial Intelligence

> **The Technical Challenge:** Standard RAG applications are synchronous. If a user uploads 50 documents (e.g., 10-K filings), the web server hangs while waiting for embeddings, leading to timeouts (504 Errors) and crashes under load.
> **The Solution:** MarketPulse is an **Asynchronous RAG Engine**. It separates ingestion from processing using a **Go** gateway and **Redis** buffer, allowing it to ingest massive financial datasets instantly while a **Python** brain processes them in the background.

---

## 🏗 Architecture

The system is designed to handle **burst traffic** (like Earnings Season) without dropping requests.

```mermaid
graph LR
    subgraph "High-Speed Ingestion Layer"
        Client["Client / Feed"] -- "POST /ingest (JSON)" --> Gateway["Go API Gateway"]
    end
    Gateway -- "LPUSH (Instant)" --> Redis["Redis Queue"]
    
    subgraph "Async Processing Layer"
        Redis -- "BRPOP (Blocking)" --> Worker["Python AI Worker"]
        Worker -- "Embed & Tag" --> OpenAI
        Worker -- "Upsert w/ Metadata" --> Qdrant[("Qdrant Vector DB")]
    end

```

### Core Components

| Service | Tech Stack | Role | Why this tech? |
| --- | --- | --- | --- |
| **The Gateway** | **Go (Fiber)** | Ingestion | Handles 10k+ concurrent requests/sec. Eliminates the "GIL" bottleneck of Python servers. |
| **The Buffer** | **Redis** | Message Queue | Acts as a "Shock Absorber." If OpenAI latency spikes, the queue grows, but the server stays up. |
| **The Brain** | **Python 3.12** | Semantic Processing | Uses `uv` for fast dependency management. Handles the complex financial logic (Chunking/Embedding). |
| **The Memory** | **Qdrant** | Vector Database | Stores vectors with **Metadata Passports** (Region, Topic) for surgical retrieval. |

---

## 💼 The Business Case: "The Wisdom & The Wire"

I applied this architecture to solve a critical problem in FinTech: **Information Overload.**

* **The Problem:** Financial analysts cannot process real-time news ("The Wire") and cross-reference it with deep fundamental strategy ("The Wisdom") without latency or hallucination.
* **The Implementation:**
* **The Wire:** The Go Gateway ingests live RSS/News feeds instantly.
* **The Wisdom:** The Python Worker indexes static PDFs (e.g., *The Intelligent Investor*).
* **The Result:** A system that can answer: *"Based on Benjamin Graham's principles, how should I react to today's inflation news?"*



---

## 🚀 Key Features

* **Non-Blocking I/O:** The Go Gateway acknowledges data receipt in microseconds (`202 Accepted`), preventing client timeouts during large file uploads.
* **Metadata Passporting:** Every document is tagged with `region` (US/India) and `topic`. The AI knows not to apply US Tax Law to Indian Stocks.
* **Smart Chunking:** Uses context-aware splitters (RecursiveCharacter) to keep financial concepts intact across page breaks.
* **Dockerized:** Entire stack spins up with a single compose command.

---

## 🛠️ Getting Started

### Prerequisites

* Docker & Docker Compose
* OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/onslaught7/market-pulse-engine.git
cd market-pulse-engine

```


2. **Set Environment Variables**
Create a `.env` file in the root:
```env
OPENAI_API_KEY=sk-your-key-here
REDIS_HOST=redis
QDRANT_HOST=qdrant

```


3. **Launch the System**
```bash
docker-compose up --build

```



---

## ⚡ Usage

### 1. Ingest a Document (Simulate High Load)

Send a request to the Go Gateway. It will respond instantly, proving the async architecture works.

```bash
curl -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "analyst_01",
    "document_id": "report_2024_Q3",
    "content": "Inflation remains sticky at 6%...",
    "metadata": {"region": "global", "type": "news"}
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

The Python worker picks up the task asynchronously:

```text
[Worker] Processing report_2024_Q3...
[Worker] Type: 'news' | Region: 'global'
[Worker] Indexed in 'wire' collection. Time: 0.4s

```

---

## 🧠 Engineering Decisions

**Why Go for Ingestion?**
Python's GIL bottlenecks under high-concurrency HTTP loads. When processing 100+ concurrent PDF uploads, standard Python servers often crash or time out. Go handles these connections with goroutines using a fraction of the RAM.

**Why Qdrant instead of Pinecone?**
We need **Metadata Filtering** ("Show me only Indian stocks") to prevent the AI from hallucinating across markets. Qdrant's payload filtering is blazing fast and runs locally in Docker, allowing for a fully self-hosted stack.

---

## 📜 License

MIT