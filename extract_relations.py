import itertools

from helpers import pars_karamazov, pars_solitude, write_json
from prompts import (
    relation_extraction_prompt,
    character_mapping_prompt,
    character_description_prompt,
    relation_description_prompt,
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


def generate_relations(parsed_content: dict):
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


def generate_character_mapping(parsed_content: dict, relations: dict) -> dict:
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
            )["description"]
            character_descs[character] = char_desc
        except (json.JSONDecodeError, KeyError):
            continue
    return character_descs


def extract_character_names(relation: dict) -> tuple:
    """Extract character names from a relation's character mapping."""
    char_names = [
        list(char_map.values())[0] for char_map in relation["character_mapping"]
    ]
    return tuple(char_names)


def collect_character_descriptions(
    relations: dict, character_permutations: list
) -> dict:
    """Collect descriptions for each character pair."""
    relationship_descriptions = {perm: [] for perm in character_permutations}

    for chapter in relations.values():
        for chunk in chapter.values():
            for relation in chunk:
                relation_pair = extract_character_names(relation)

                if relation_pair in character_permutations:
                    relationship_descriptions[relation_pair].append(
                        relation["description"]
                    )

    return {k: v for k, v in relationship_descriptions.items() if v}


def process_relation_description(
    perm: tuple, descriptions: list, prompt_template: str
) -> dict:
    """Process a single relation description using the provided prompt template."""
    prompt = (
        prompt_template.replace("_character_A_", perm[0])
        .replace("_character_B_", perm[1])
        .replace("_descriptions_", "\n-".join(descriptions))
    )

    response = generate_respons(prompt)
    
    try:
        raw_message = json.loads(response.choices[0].message.function_call.arguments)[
            "message"
        ]
        return {
            "from": perm[0],
            "to": perm[1],
            "description": raw_message,
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "from": perm[0],
            "to": perm[1],
            "description": "",
        }


def generate_character_relation_descriptions(
    relations: dict, characters: dict, relation_description_prompt: str
) -> list:
    """Generate descriptions for character relationships."""
    character_permutations = list(itertools.permutations(list(characters.keys()), 2))
    relation_examples = collect_character_descriptions(
        relations, character_permutations
    )
    relation_descriptions = []
    for perm, descs in tqdm(
        relation_examples.items(), desc="Relationship Descriptions"
    ):
        relation = process_relation_description(
            perm, descs, relation_description_prompt
        )
        relation_descriptions.append(relation)

    return relation_descriptions


import os
import json


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    if GRAPHENV in ["karamazov", "solitude"]:
        file_paths = {
            "karamazov": "data/brothers-karamazov/karamazov.txt",
            "solitude": "data/one-hundred-years-of-solitude/solitude.pdf",
        }

        # Create tmp directory path
        base_dir = os.path.dirname(file_paths[GRAPHENV])
        tmp_dir = os.path.join(base_dir, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        # Define paths for intermediate files
        tmp_paths = {
            "parsed_content": os.path.join(tmp_dir, "parsed_content.json"),
            "relations": os.path.join(tmp_dir, "relations.json"),
            "char_relations": os.path.join(tmp_dir, "character_relations.json"),
            "characters": os.path.join(tmp_dir, "characters.json"),
        }

        # Parse content or load from cache
        if os.path.exists(tmp_paths["parsed_content"]):
            parsed_content = read_json(tmp_paths["parsed_content"])
        else:
            parse_functions = {"karamazov": pars_karamazov, "solitude": pars_solitude}
            parsed_content = parse_functions[GRAPHENV](file_paths[GRAPHENV])
            write_json(tmp_paths["parsed_content"], parsed_content)

        # Generate or load relations
        if os.path.exists(tmp_paths["relations"]):
            relations = read_json(tmp_paths["relations"])
        else:
            relations = generate_relations(parsed_content)
            relations = generate_character_mapping(parsed_content, relations)
            write_json(tmp_paths["relations"], relations)

        # Generate or load character descriptions
        if os.path.exists(tmp_paths["characters"]):
            characters = read_json(tmp_paths["characters"])
        else:
            characters = generate_character_descriptions(
                book_title=parsed_content["title"], relations=relations
            )
            write_json(tmp_paths["characters"], characters)

        # Generate or load relation descriptions
        if os.path.exists(tmp_paths["char_relations"]):
            relation_descriptions = read_json(tmp_paths["char_relations"])
        else:
            relation_descriptions = generate_character_relation_descriptions(
                relations, characters, relation_description_prompt
            )
            write_json(tmp_paths["char_relations"], relation_descriptions)

        # Combine all data into final output
        graph_data = {
            "relations": relations,
            "characters": characters,
            "character_relations": relation_descriptions,
        }

        # Write final output
        json_path = os.path.join(base_dir, "graph_data.json")
        write_json(json_path, graph_data)


if __name__ == "__main__":
    main()
