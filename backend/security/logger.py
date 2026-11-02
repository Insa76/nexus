from datetime import datetime

FILE = "nexus_logs.txt"


def log(action, result):

    line = f"{datetime.now()} | {action} | {result}"

    # ✅ guardar archivo
    with open(FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    # ✅ mostrar en consola (nuevo)
    print(line)
