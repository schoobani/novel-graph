import re
from dataclasses import asdict, dataclass
from typing import Any

from pypdf import PdfReader
from tqdm import tqdm

from helpers import chunk_text, normalize_characters


@dataclass
class Chapter:
    title: str
    text: dict[str, str]


@dataclass
class BookContent:
    chapters: dict[str, Chapter]


@dataclass
class Book:
    title: str
    content: BookContent


def parse_karamazov(path: str) -> Any:
    """
    Parse the book "The Brothers Karamazov" by Fyodor Dostoevsky
    and return a properly typed Book object.
    """
    with open(path, "r", encoding="utf-8") as f:
        corpus = f.read()

    corpus = normalize_characters(corpus)
    corpus = corpus.split("THE END")[0]
    content = corpus.split("Chapter")

    chapters: dict[str, Chapter] = {}
    for i, chapter in enumerate(content[1:], start=1):
        lines = chapter.split("\n")
        title = "\n".join(lines[:2]).strip()
        body = "\n".join(lines[2:]).strip()

        # Convert chunked text into TextSection objects
        text_sections: dict[str, str] = {}
        for idx, text in enumerate(chunk_text(body)):
            text_sections[str(idx)] = text

        chapters[str(i)] = Chapter(title=title, text=text_sections)

    return asdict(
        Book(title="The Brothers Karamazov", content=BookContent(chapters=chapters))
    )


def parse_solitude(path: str) -> Any:
    """
    Parse the book "One Hundred Years of Solitude" by Gabriel García Márquez
    and return a properly typed Book object.
    """
    reader = PdfReader(path)
    corpus = ""
    for page in tqdm(reader.pages):
        page_text = page.extract_text().encode("utf-8").decode("utf-8")
        corpus += "\n" + page_text

    replace_strs = [
        "ONE HUNDRED YEARS OF SOLITUDE",
        "GABRIEL GARCIA MARQUEZ",
        """Dear Friends, this is a backup copy of the original works in my personal library. I had a bad luck in get ting back the books \nI lend to my friends. I am trying to make the text in  digital form to ensure that I am not going to loose  a n y  o f  t h e m .  A s  I  \nhave an original printed edition, its sure that the w riter/publisher already got their share. As on my kno wledge there is no \nlegal issues in giving my library collections to my  friends, those who loves to read. Kindly delete this f ile after reading and \nit would be taken as I got the book back.  \nWith Thanks and regards your friend Antony. mail me to  antonyboban@gmail.com""",
    ]

    for rstr in replace_strs:
        corpus = corpus.replace(rstr, "")

    corpus = normalize_characters(corpus)

    chapters: dict[str, Chapter] = {}
    for chap in corpus.split("Chapter")[1:]:
        chap_id = int(chap.strip()[:3].strip())
        chap = chap.strip()[3:].strip()
        chap = re.sub(r"\s*\d+\s*", "\n\n\n", chap)

        text_sections: dict[str, str] = {}
        for i, chunk in enumerate(chap.split("\n\n\n")):
            if chunk.strip():
                text_sections[str(i)] = chunk.strip()

        chapters[str(chap_id)] = Chapter(title=f"Chapter {chap_id}", text=text_sections)

    return asdict(
        Book(
            title="One Hundred Years of Solitude",
            content=BookContent(chapters=chapters),
        )
    )


def parse_war_peace(path: str) -> Any:
    """
    Parse the book "War and Peace" by Leo Tolstoy
    and return a properly typed Book object.
    """
    with open(path, "r", encoding="utf-8") as f:
        corpus = f.read()

    corpus = normalize_characters(corpus)
    content = corpus.split("CHAPTER")

    chapters: dict[str, Chapter] = {}
    for i, chapter in enumerate(content[1:], start=1):
        lines = chapter.split("\n")
        body = "\n".join(lines).strip()

        text_sections: dict[str, str] = {}
        for idx, text in enumerate(chunk_text(body)):
            text_sections[str(idx)] = text

        chapters[str(i)] = Chapter(title=f"Chapter {i}", text=text_sections)

    return asdict(Book(title="War and Peace", content=BookContent(chapters=chapters)))


def parse_master_and_margarita(path: str) -> Any:
    """
    Parse the book "The Master and Margarita"
    and return a properly typed Book object.
    """
    # Placeholder implementation
    return Book(title="The Master and Margarita", content=BookContent(chapters={}))
