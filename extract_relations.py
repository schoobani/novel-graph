import re
from helpers import pars_karamazov, pars_solitude, write_json
from prompts import relation_extraction_prompt
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

        for i, paragraph in tqdm(chapter["text"].items()):
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


def main():
    if GRAPHENV in ["karamazov", "solitude"]:
        file_paths = {
            "karamazov": "data/brothers-karamazov/karamazov.txt",
            "solitude": "data/one-hundred-years-of-solitude/solitude.pdf",
        }

        parse_functions = {"karamazov": pars_karamazov, "solitude": pars_solitude}

        parsed_content = parse_functions[GRAPHENV](file_paths[GRAPHENV])
        relations = extract_relations(parsed_content)
        json_path = os.path.join(
            os.path.dirname(file_paths[GRAPHENV]), f"relations.json"
        )
        write_json(json_path, relations)


if __name__ == "__main__":
    main()
