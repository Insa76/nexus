import os
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import docx

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection("nexus_memory")


def read_file(path):
    ext = path.lower().split(".")[-1]

    if ext == "txt":
        return open(path, encoding="utf-8", errors="ignore").read()

    if ext == "pdf":
        reader = PdfReader(path)
        return "\n".join(p.extract_text() or "" for p in reader.pages)

    if ext == "docx":
        d = docx.Document(path)
        return "\n".join(p.text for p in d.paragraphs)

    return ""


def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]


def index_folder(folder):
    for root, _, files in os.walk(folder):
        for f in files:
            if f.endswith((".pdf", ".txt", ".docx")):
                path = os.path.join(root, f)
                print("Indexando:", path)

                content = read_file(path)
                chunks = chunk_text(content)

                for i, chunk in enumerate(chunks):
                    emb = model.encode(chunk).tolist()

                    collection.add(
                        documents=[chunk],
                        embeddings=[emb],
                        ids=[f"{path}_{i}"],
                        metadatas=[{"path": path}]
                    )
