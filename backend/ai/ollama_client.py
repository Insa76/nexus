import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_ollama(prompt):

    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload)

    data = r.json()

    return data["response"]