import json
import os


def write_jsonl(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def chunk_text(text: str, chunk_size: int = 2500) -> list[str]:
    """
    Split the text into chunks of a specified size
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for paragraph in paragraphs:
        if current_length + len(paragraph) <= chunk_size:
            current_chunk.append(paragraph)
            current_length += len(paragraph) + 1  # Account for newline
        else:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            current_chunk = [paragraph]
            current_length = len(paragraph) + 1

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def normalize_characters(text):
    return (
        text.replace("ú", "u")
        .replace("í", "i")
        .replace("é", "e")
        .replace("á", "a")
        .replace("ó", "o")
        .replace("Ú", "U")
        .replace("Í", "I")
        .replace("É", "E")
        .replace("Á", "A")
        .replace("Ó", "O")
        .replace("ï", "i")
        .replace("ü", "u")
        .replace("ö", "o")
        .replace("ä", "a")
        .replace("Ë", "E")
        .replace("ÿ", "y")
    )


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, data, indent=4):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)
