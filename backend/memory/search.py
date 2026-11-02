import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection("nexus_memory")


def search_memory(query, k=4):
    emb = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[emb],
        n_results=k
    )

    docs = results.get("documents", [[]])[0]

    return "\n".join(docs)
