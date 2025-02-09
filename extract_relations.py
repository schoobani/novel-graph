import re

from helpers import pars_karamazov, pars_solitude, write_json
from prompts import (
    relation_extraction_prompt,
    character_mapping_prompt,
    character_description_prompt,
)
from openai import OpenAI
import sys
import os
import json
from tqdm import tqdm

GRAPHENV = sys.argv[1]
openai_key = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=openai_key)


def generate_respons(prompt):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        functions=[
            {
                "name": "output_message",
                "description": "Outputs a message in JSON format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to output",
                        }
                    },
                    "required": ["message"],
                },
            }
        ],
        function_call={"name": "output_message"},
    )


def extract_relations(parsed_content: dict):
    relations = {}
    book_title = parsed_content["title"]
    content = parsed_content["content"]

    for chapter_num, chapter in list(content.items())[:1]:
        relations[chapter_num] = {}

        for i, paragraph in tqdm(
            list(chapter["text"].items())[:1], desc=f"Relations Chapter {chapter_num}"
        ):
            relations[chapter_num][i] = []
            prompt = relation_extraction_prompt.replace(
                "_book_title_", book_title
            ).replace("_book_paragraph_", paragraph)

            # Try fetching relations with retries
            for _ in range(2):
                response = generate_respons(prompt)
                try:
                    relations[chapter_num][i].extend(
                        json.loads(
                            json.loads(
                                response.choices[0].message.function_call.arguments
                            )["message"]
                        )["relations"]
                    )
                    break
                except (json.JSONDecodeError, KeyError):
                    continue
    return relations


def map_characters(parsed_content: dict, relations: dict) -> dict:
    for chpater_idx, chapter in relations.items():
        for chunk_idx, chunk in tqdm(
            chapter.items(), desc=f"Mapping Characters Chapter {chpater_idx}"
        ):
            for relation in chunk:
                prompt = (
                    character_mapping_prompt.replace(
                        "_book_title_", parsed_content["title"]
                    )
                    .replace(
                        "_book_paragraph_",
                        parsed_content["content"][chpater_idx]["text"][chunk_idx],
                    )
                    .replace("_character_A_", relation["from"])
                    .replace("_character_B_", relation["to"])
                )
                response = generate_respons(prompt)
                try:
                    relation["character_mapping"] = json.loads(
                        json.loads(response.choices[0].message.function_call.arguments)[
                            "message"
                        ]
                    )["relations"]
                except (json.JSONDecodeError, KeyError):
                    continue
    return relations


def extract_characters(relations):
    return {
        char.strip()
        for chapter in relations.values()
        for chunk in chapter.values()
        for r in chunk
        for c in r["character_mapping"]
        for char in list(c.values())[0].split(",")
    }


def generate_character_descriptions(book_title: str, relations: dict) -> dict:
    characters = extract_characters(relations)
    character_descs = {}
    for character in tqdm(characters, desc=f"Character Descriptions"):
        prompt = character_description_prompt.replace(
            "_book_title_", book_title
        ).replace("_character_name_", character)
        response = generate_respons(prompt)
        try:
            char_desc = json.loads(
                json.loads(response.choices[0].message.function_call.arguments)[
                    "message"
                ]
            )["desc"]
            character_descs[character] = char_desc
        except (json.JSONDecodeError, KeyError):
            continue
    return character_descs


def main():
    if GRAPHENV in ["karamazov", "solitude"]:
        file_paths = {
            "karamazov": "data/brothers-karamazov/karamazov.txt",
            "solitude": "data/one-hundred-years-of-solitude/solitude.pdf",
        }

        parse_functions = {"karamazov": pars_karamazov, "solitude": pars_solitude}

        parsed_content = parse_functions[GRAPHENV](file_paths[GRAPHENV])
        relations = extract_relations(parsed_content)
        relations = map_characters(parsed_content, relations)
        characters = generate_character_descriptions(
            book_title=parsed_content["title"], relations=relations
        )

        graph_data = {
            "relations": relations,
            "characters": characters,
        }

        json_path = os.path.join(
            os.path.dirname(file_paths[GRAPHENV]), f"graph_data.json"
        )
        write_json(json_path, graph_data)


if __name__ == "__main__":
    main()
