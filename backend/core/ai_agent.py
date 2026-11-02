import requests


OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_agent(
    prompt,
    model="llama3"
):

    payload = {

        "model": model,

        "prompt": prompt,

        "stream": False
    }

    res = requests.post(
        OLLAMA_URL,
        json=payload
    )

    data = res.json()

    return data.get(
        "response",
        ""
    )