import ollama

SYSTEM = """
Evaluá si la ejecución fue exitosa.

Si todo ok → OK
Si hubo problema → FAIL
"""


def evaluate(result_text):

    res = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": result_text}
        ]
    )

    return "OK" in res["message"]["content"].upper()
