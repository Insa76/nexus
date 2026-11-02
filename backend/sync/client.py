import requests

SYNC_URL = "http://192.168.0.15:8000/sync"  # IP del HUB


def push_memory(text):

    try:
        requests.post(SYNC_URL + "/push", json={"content": text})
    except:
        pass


def pull_memory():

    try:
        r = requests.get(SYNC_URL + "/pull")
        return r.json()["items"]
    except:
        return []
