import math


def fake_embedding(text):

    text = text.lower()

    vector = []

    for c in text[:128]:

        vector.append(
            ord(c) / 255
        )

    while len(vector) < 128:
        vector.append(0)

    return vector


def cosine_similarity(a, b):

    dot = sum(x*y for x,y in zip(a,b))

    norm_a = math.sqrt(
        sum(x*x for x in a)
    )

    norm_b = math.sqrt(
        sum(x*x for x in b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0

    return dot / (
        norm_a * norm_b
    )