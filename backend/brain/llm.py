import requests

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

def ask_llm(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]