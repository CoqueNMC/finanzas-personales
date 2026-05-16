"""Generación de IDs únicos. Centralizado para facilitar cambio de estrategia."""
import time, random, string

def generate_id(prefix: str = "") -> str:
    ts = time.strftime("%y%m%d%H%M%S")
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{ts}_{rand}" if prefix else f"{ts}_{rand}"
