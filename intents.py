# intents module for intent detection
import re
import unicodedata
from typing import Tuple, Optional


def normalize(text: str) -> str:
    text = text.lower()

    # Remove accents
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


INTENTS = {
    "GREETING": [
        "oi",
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite",
    ],
    "SERVICES": [
        "servicos",
        "servico",
        "oferecem",
        "oferece",
        "oferecer",
        "o que voces oferecem",
        "quais servicos",
    ],
    "PRICING": [
        "preco",
        "precos",
        "valor",
        "valores",
        "quanto custa",
    ],
    "SUPPORT": [
        "suporte",
        "ajuda",
        "problema",
        "erro",
    ],
    "HUMAN": [
        "humano",
        "atendente",
        "pessoa",
        "falar com alguem",
    ],
}


def detect_intent(text: str) -> Tuple[Optional[str], float]:
    normalized = normalize(text)

    best_intent = None
    best_score = 0.0

    if not normalized:
        return None, 0.0

    for intent, patterns in INTENTS.items():
        for pattern in patterns:
            if pattern in normalized:
                score = len(pattern) / len(normalized)
                if score > best_score:
                    best_score = score
                    best_intent = intent

    return best_intent, round(best_score, 2)