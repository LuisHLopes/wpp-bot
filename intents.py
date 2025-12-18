# intents.py
import re
import unicodedata

def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


INTENTS = {
    "GREETING": [
        "oi", "ola", "bom dia", "boa tarde", "boa noite"
    ],
    "SERVICES": [
        "servicos", "servico", "oferecem", "oferece",
        "o que voces oferecem", "quais servicos"
    ],
    "PRICING": [
        "preco", "precos", "valor", "valores", "quanto custa"
    ],
    "SUPPORT": [
        "suporte", "ajuda", "problema", "erro"
    ],
    "HUMAN": [
        "humano", "atendente", "pessoa", "falar com alguem"
    ],
}


def detect_intent(text: str):
    normalized = normalize(text)

    for intent, patterns in INTENTS.items():
        for pattern in patterns:
            if pattern in normalized:
                return intent

    return None
