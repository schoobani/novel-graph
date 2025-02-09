import json
from pypdf import PdfReader
from tqdm import tqdm
import re
import os


def pars_karamazov(book_path: str) -> dict[int, dict[str, list[str]]]:
    """
    Parse the book "The Brothers Karamazov" by Fyodor Dostoevsky
    and return a dictionary with chunked content.
    """
    with open(book_path, "r", encoding="utf-8") as f:
        corpus = f.read()

    corpus = corpus.split("THE END")[0]
    content = corpus.split("Chapter")

    parsed_content = {}
    for i, chapter in enumerate(content[1:], start=1):
        lines = chapter.split("\n")
        title = "\n".join(lines[:2]).strip()
        body = "\n".join(lines[2:]).strip()
        parsed_content[i] = {"title": title, "content": chunk_text(body)}

    json_path = os.path.join(os.path.dirname(book_path), "karamazov.json")
    write_json(json_path, parsed_content)


def pars_solitude(book_path) -> dict:
    """
    Parse the book "One Hundred Years of Solitude" by Gabriel García Márquez
    and return a dictionary content of the book.
    """
    reader = PdfReader(book_path)
    doc = ""
    for page in tqdm(reader.pages):
        page_text = page.extract_text().encode("utf-8").decode("utf-8")
        doc += "\n" + page_text

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
        doc = doc.replace(rstr, "")

    content = {}
    for chap in doc.split("Chapter")[1:]:
        chap_id = int(chap.strip()[:3].strip())
        chap = chap.strip()[3:].strip()
        chap = re.sub(r"\s*\d+\s*", "\n\n\n", chap)
        content[chap_id] = {"title": f"Chapter {chap_id}", "content": {}}
        for i, page in enumerate(chap.split("\n\n\n")):
            if page.strip():
                content[chap_id]["content"][i] = page

    json_path = os.path.join(os.path.dirname(book_path), "solitude.json")
    write_json(json_path, content)


def write_json(filename, data, indent=4):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def chunk_text(text: str, chunk_size: int = 2500) -> list[str]:
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
