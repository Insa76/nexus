import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime
from sync.client import push_memory

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection("nexus_personal")


def save_memory(text, meta=None):

    emb = model.encode(text).tolist()

    collection.add(
        documents=[text],
        embeddings=[emb],
        ids=[str(datetime.now().timestamp())],
        metadatas=[meta or {}]
    )

    push_memory(text)
