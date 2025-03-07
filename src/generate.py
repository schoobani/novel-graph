import itertools
import json
import logging
import os
import sys
from collections import Counter

import numpy as np
from openai import OpenAI
from tqdm import tqdm

from helpers import (
    read_json,
    write_json,
)
from parsers import (
    parse_karamazov,
    parse_master_and_margarita,
    parse_solitude,
    parse_war_peace,
)
from prompts import (
    character_description_prompt,
    character_mapping_prompt,
    name_group_prompt,
    relation_description_prompt,
    relation_extraction_prompt,
)

GRAPHENV = sys.argv[1]
openai_key = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=openai_key)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


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
    relations: dict[str, dict[str, list[dict]]] = {}
    book_title = parsed_content["title"]
    content = parsed_content["content"]["chapters"]

    for chapter_num, chapter in list(content.items()):
        relations[chapter_num] = {}

        for i, paragraph in tqdm(
            list(chapter["text"].items()), desc=f"Relations Chapter {chapter_num}"
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
                        parsed_content["content"]["chapters"][chpater_idx]["text"][
                            chunk_idx
                        ],
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


def extract_common_characters(relations, percentile=90):
    characters = []
    for chapter in relations.values():
        for chunk in chapter.values():
            for r in chunk:
                if "character_mapping" in r:
                    for c in r["character_mapping"]:
                        character = list(c.values())[0]
                        if isinstance(character, str):
                            characters.extend(
                                char.strip().lower() for char in character.split(",")
                            )

    counts = Counter(characters)
    threshold = np.percentile(list(counts.values()), percentile)
    return {char for char, count in counts.items() if count >= threshold}


def generate_character_descriptions(book_title: str, relations: dict) -> dict:
    characters = extract_common_characters(relations)
    character_descs = {}
    for character in tqdm(characters, desc="Character Descriptions"):
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
        list(char_map.values())[0]
        for char_map in relation.get("character_mapping", [])
        if char_map
    ]
    return tuple(item.lower() for item in char_names if isinstance(item, str) and item)


def collect_character_descriptions(
    relations: dict, character_permutations: list
) -> dict:
    """Collect descriptions for each character pair."""
    relationship_descriptions: dict[tuple, list] = {
        perm: [] for perm in character_permutations
    }

    for chapter in relations.values():
        for chunk in chapter.values():
            for relation in chunk:
                relation_pair = extract_character_names(relation)
                if relation_pair in character_permutations:
                    relationship_descriptions[relation_pair].append(
                        relation["description"]
                    )
    return {k: v for k, v in relationship_descriptions.items() if v}


def generate_relation_description(
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
        relation = generate_relation_description(
            perm, descs, relation_description_prompt
        )
        relation_descriptions.append(relation)

    return relation_descriptions


def generate_name_mapping(characters: list, book_title: str) -> dict:
    """Generate a single level of name mapping."""
    prompt = name_group_prompt.replace(
        "_character_names_",
        "\n".join(sorted(characters)),
    ).replace("_book_title_", book_title)

    response = generate_respons(prompt)
    try:
        name_mapping = json.loads(
            json.loads(response.choices[0].message.function_call.arguments)["message"]
        )
        logger.info(f"Mapping complete - mapped {len(name_mapping)} names")
        return name_mapping
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to generate name mapping: {str(e)}")
        return {}


def merge_mappings(
    prev_mapping: dict[str, list[str]], next_mapping: dict[str, list[str]]
) -> dict[str, list[str]]:
    """Merge mappings to create comprehensive character name groups."""
    prev_mapping = {
        k.lower(): [i.lower() for i in v if isinstance(i, str)]
        for k, v in prev_mapping.items()
    }
    next_mapping = {
        k.lower(): [i.lower() for i in v if isinstance(i, str)]
        for k, v in next_mapping.items()
    }

    merged: dict[str, list[str]] = {}

    for k, v in next_mapping.items():
        merged[k] = []
        for item in prev_mapping.get(k, []):
            merged[k].append(item.lower())
        for element in v:
            for item in prev_mapping.get(element, []):
                merged[k].append(item.lower())

    for k, v in prev_mapping.items():
        if k not in merged:
            merged[k] = v

    return merged


def generate_name_groups(characters: list, book_title: str) -> dict:
    logger.info(f"Starting name group generation with {len(characters)} characters")

    # Step 1: First level mapping - group similar names
    logger.debug("Step 1: Generating first level name mapping")
    first_mapping = generate_name_mapping(characters, book_title)
    write_json(
        os.path.join(
            os.path.dirname(os.path.dirname(book_title)), "tmp/first_mapping.json"
        ),
        first_mapping,
    )

    # Step 2: Second level mapping - consolidate groups
    logger.debug("Step 2: Generating second level name mapping")
    second_mapping = generate_name_mapping(
        [k for k in first_mapping.keys()], book_title
    )
    write_json(
        os.path.join(
            os.path.dirname(os.path.dirname(book_title)), "tmp/second_mapping.json"
        ),
        second_mapping,
    )
    name_groups = merge_mappings(first_mapping, second_mapping)

    # Calculate mapping coverage
    all_mapped_names = {name for group in name_groups.values() for name in group}
    all_mapped_names.update(name_groups.keys())
    mapping_percentage = (len(all_mapped_names) / len(characters)) * 100
    diff = set(characters) - all_mapped_names

    for char in diff:
        name_groups[char] = []

    logger.info(f"Final name groups generated - {len(name_groups)} groups created")
    logger.info(f"Mapping coverage: {mapping_percentage:.2f}% of original characters")

    return name_groups


def get_paths(graphenv):
    file_paths = {
        "karamazov": "data/brothers-karamazov/karamazov.txt",
        "solitude": "data/one-hundred-years-of-solitude/solitude.pdf",
        "war-and-peace": "data/war-and-peace/war-and-peace.txt",
        "master-and-margarita": "data/master-and-margarita/master-and-margarita.pdf",
    }
    base_dir = os.path.dirname(file_paths[graphenv])
    tmp_dir = os.path.join(base_dir, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    return {
        "input": file_paths[graphenv],
        "base": base_dir,
        "tmp": {
            "parsed_content": os.path.join(tmp_dir, "parsed_content.json"),
            "relations": os.path.join(tmp_dir, "relations.json"),
            "char_relations": os.path.join(tmp_dir, "character_relations.json"),
            "characters": os.path.join(tmp_dir, "characters.json"),
            "name_groups": os.path.join(tmp_dir, "name_groups.json"),
        },
    }


def get_or_generate(path, generate_fn, *args):
    if os.path.exists(path):
        logger.info(f"Reading from cache: {os.path.basename(path)}")
        return read_json(path)

    logger.info(f"Generating new: {os.path.basename(path)}")
    data = generate_fn(*args)
    write_json(path, data)
    return data


def process_parsed_content(paths, graphenv):
    parse_functions = {
        "karamazov": parse_karamazov,
        "solitude": parse_solitude,
        "war-and-peace": parse_war_peace,
        "master-and-margarita": parse_master_and_margarita,
    }
    return get_or_generate(
        paths["tmp"]["parsed_content"], parse_functions[graphenv], paths["input"]
    )


def process_relations(paths, parsed_content):
    def generate_full_relations(content):
        rels = generate_relations(content)
        return generate_character_mapping(content, rels)

    return get_or_generate(
        paths["tmp"]["relations"], generate_full_relations, parsed_content
    )


def process_characters(paths, parsed_content, relations):
    return get_or_generate(
        paths["tmp"]["characters"],
        generate_character_descriptions,
        parsed_content["title"],
        relations,
    )


def process_char_relations(paths, relations, characters):
    return get_or_generate(
        paths["tmp"]["char_relations"],
        generate_character_relation_descriptions,
        relations,
        characters,
        relation_description_prompt,
    )


def process_name_groups(
    paths: dict[str, dict[str, str]], characters: list[str], book_title: str
) -> dict:
    return get_or_generate(
        paths["tmp"]["name_groups"],
        generate_name_groups,
        characters,
        book_title,
    )


def main():
    if GRAPHENV not in [
        "karamazov",
        "solitude",
        "war-and-peace",
        "master-and-margarita",
    ]:
        return

    paths = get_paths(GRAPHENV)
    parsed_content = process_parsed_content(paths, GRAPHENV)
    relations = process_relations(paths, parsed_content)
    characters = process_characters(paths, parsed_content, relations)
    relation_descriptions = process_char_relations(paths, relations, characters)
    name_groups = process_name_groups(
        paths,
        characters={char.lower() for char in list(characters.keys())},
        book_title=parsed_content["title"],
    )

    graph_data = {
        "relations": relations,
        "characters": characters,
        "character_relations": relation_descriptions,
        "name_groups": name_groups,
    }

    json_path = os.path.join(paths["base"], "data.json")
    write_json(json_path, graph_data)
    logger.info(f"Final graph data written to {json_path}")


if __name__ == "__main__":
    main()
