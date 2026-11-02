import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection("nexus_personal")


def recall(query, k=3):

    emb = model.encode(query).tolist()

    res = collection.query(
        query_embeddings=[emb],
        n_results=k
    )

    docs = res.get("documents", [[]])[0]

    return "\n".join(docs)
