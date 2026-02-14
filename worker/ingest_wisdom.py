import os
import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_openai import OpenAIEmbeddings


from config import settings


# The financial passport metadata schema
LIBRARY_MAP = {
    "the_intelligent_investor.pdf": {
        "title": "The Intelligent Investor",
        "author": "Benjamin Graham",
        "region": "global",
        "topic": "value_investing"
    },
    "the_psychology_of_money.pdf": {
        "title": "The Psychology of Money",
        "author": "Morgan Housel",
        "region": "global",
        "topic": "psychology"
    },
    "stocks_to_riches.pdf": {
        "title": "Stocks to Riches",
        "author": "Parag Parikh",
        "region": "india",
        "topic": "growth_investing"
    },
    "one_up_on_wall_street.pdf": {
        "title": "One Up On Wall Street",
        "author": "Peter Lynch",
        "region": "us",
        "topic": "retail_strategy"
    }
}


def ingest_books():
    print(f"[*] Connecting to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}...")

    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

    if not client.collection_exists(settings.COLLECTION_WISDOM):
        print(f" [!] Collection '{settings.COLLECTION_WISDOM}' not found. Creating...")
        client.create_collection(
            collection_name=settings.COLLECTION_WISDOM,
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
        )

    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set.")
    # The embedding fails if I ever changet he model (1536 = 1536)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]    
    )

    # path finding
    data_folder = os.path.join("..", "data", "books")
    if not os.path.exists(data_folder):
        data_folder = os.path.join("data", "books")

    print(f"[*] Reading books from: {data_folder}")

    for filename, meta in LIBRARY_MAP.items():
        file_path = os.path.join(data_folder, filename)

        if not os.path.exists(file_path):
            print(f" [!] File MISSING: {filename} (Skipping)")
            continue

        print(f" [*] Processing: {meta['title']}...")

        try:
            loader = PyPDFLoader(file_path)
            
            pages = loader.load()
            print(f"     -> Loaded {len(pages)} pages.")

            chunks = splitter.split_documents(pages)
            print(f"     -> Created {len(chunks)} chunks.")

            batch_size = 50
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                texts = [c.page_content for c in batch]

                vectors = embeddings.embed_documents(texts)

                points = []
                for j, text in enumerate(texts):
                    unique_string = f"{filename}_chunk_{i+j}"
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

                    clean_text = text.replace("\x00", "").strip()

                    payload = meta.copy()
                    payload["page_content"] = clean_text
                    payload["source_type"] = "book"

                    points.append(models.PointStruct(
                        id=point_id,
                        vector=vectors[j],
                        payload=payload
                    ))

                client.upsert(collection_name=settings.COLLECTION_WISDOM, points=points)
                print(f"     -> Batch {i//batch_size + 1} indexed.")
            
            print(f" [v] Success: {meta['title']} ingested.")
                
        except Exception as e:
            print(f" [!] Failed to process {filename}: {str(e)}")


if __name__ == "__main__":
    ingest_books()