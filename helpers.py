import json
from pypdf import PdfReader
from tqdm import tqdm
import re
import os


def parse_karamazov(book_path: str) -> dict[int, dict[str, list[str]]]:
    """
    Parse the book "The Brothers Karamazov" by Fyodor Dostoevsky
    and return a dictionary with chunked content.
    """
    with open(book_path, "r", encoding="utf-8") as f:
        corpus = f.read()

    corpus = normalize_characters(corpus)
    corpus = corpus.split("THE END")[0]
    content = corpus.split("Chapter")

    parsed_content = {}
    for i, chapter in enumerate(content[1:], start=1):
        lines = chapter.split("\n")
        title = "\n".join(lines[:2]).strip()
        body = "\n".join(lines[2:]).strip()
        parsed_content[i] = {"title": title, "text": chunk_text(body)}

    final_content = {
        "title": "The Brothers Karamazov",
        "content": parsed_content,
    }
    return final_content


def parse_solitude(book_path) -> dict:
    """
    Parse the book "One Hundred Years of Solitude" by Gabriel García Márquez
    and return a dictionary content of the book.
    """
    reader = PdfReader(book_path)
    corpus = ""
    for page in tqdm(reader.pages):
        page_text = page.extract_text().encode("utf-8").decode("utf-8")
        corpus += "\n" + page_text

    replace_strs = [
        "ONE HUNDRED YEARS OF SOLITUDE",
        "GABRIEL GARCIA MARQUEZ",
        """Dear Friends, this is a backup copy of the original works in my personal library. I had a bad luck in get ting back the books 
I lend to my friends. I am trying to make the text in  digital form to ensure that I am not going to loose  a n y  o f  t h e m .  A s  I  
have an original printed edition, its sure that the w riter/publisher already got their share. As on my kno wledge there is no 
legal issues in giving my library collections to my  friends, those who loves to read. Kindly delete this f ile after reading and 
it would be taken as I got the book back.  
With Thanks and regards your friend Antony. mail me to  antonyboban@gmail.com""",
    ]

    for rstr in replace_strs:
        corpus = corpus.replace(rstr, "")

    corpus = normalize_characters(corpus)

    parsed_content = {}
    for chap in corpus.split("Chapter")[1:]:
        chap_id = int(chap.strip()[:3].strip())
        chap = chap.strip()[3:].strip()
        chap = re.sub(r"\s*\d+\s*", "\n\n\n", chap)
        parsed_content[chap_id] = {"title": f"Chapter {chap_id}", "text": {}}
        for i, page in enumerate(chap.split("\n\n\n")):
            if page.strip():
                parsed_content[chap_id]["text"][i] = page

    final_content = {
        "title": "One Hundred Years of Solitude",
        "content": parsed_content,
    }
    return final_content


def parse_war_peace(book_path: str) -> dict[int, dict[str, list[str]]]:
    """Parse the book "War and Peace" by Leo Tolstoy and return a dictionary with chunked content."""
    with open(book_path, "r", encoding="utf-8") as f:
        corpus = f.read()

    corpus = normalize_characters(corpus)
    content = corpus.split("CHAPTER")

    parsed_content = {}
    for i, chapter in enumerate(content[1:], start=1):
        lines = chapter.split("\n")
        title = f"Chapter {i}"
        body = "\n".join(lines).strip()
        parsed_content[i] = {"title": title, "text": chunk_text(body)}

    final_content = {
        "title": "War and Peace",
        "content": parsed_content,
    }
    return final_content


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

    return {i: chunk for i, chunk in enumerate(chunks)}


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
