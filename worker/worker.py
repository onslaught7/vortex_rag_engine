import os
import json
import time
import redis

# 1. Connect to Redis
# We use the hostname 'redis' because Docker Compose links them by name
redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, db=0)

print(f"[*] Worker connecting to Redis at {redis_host}...")

def process_task(task_data):
    """
    Simulates the AI work (Embedding Generation)
    """
    user_id = task_data.get("user_id", "unknown")
    doc_id = task_data.get("document_id", "unknown")
    
    print(f" [x] Processing {doc_id} for User {user_id}...")
    
    # SIMULATION: This is where you would call openai.Embedding.create()
    # We sleep for 2 seconds to simulate the API latency
    time.sleep(2) 
    
    print(f" [v] Done: {doc_id} vector stored.")

def start_worker():
    print(" [*] Waiting for tasks in 'ingestion_queue'. To exit press CTRL+C")
    
    while True:
        # 2. The Blocking Pop (The Heartbeat)
        # This line blocks execution until a message appears. 
        # timeout=0 means "wait forever"
        queue, message = r.brpop("ingestion_queue", timeout=0)
        
        # 3. Process the Message
        if message:
            try:
                task_data = json.loads(message)
                process_task(task_data)
            except json.JSONDecodeError:
                print(f" [!] Error decoding JSON: {message}")
            except Exception as e:
                print(f" [!] System Error: {e}")

if __name__ == "__main__":
    # Add a small delay to let Redis start up before the worker connects
    time.sleep(3)
    start_worker()