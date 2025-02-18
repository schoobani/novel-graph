from helpers import read_json, write_json
import os
import sys
from collections import Counter
import numpy as np
from typing import Optional
import logging

GRAPHENV = sys.argv[1]

# Add logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_paths(graphenv):
    """Get environment-specific paths"""
    base_dirs = {
        "karamazov": "data/brothers-karamazov",
        "solitude": "data/one-hundred-years-of-solitude",
        "war_and_peace": "data/war_and_peace"
    }
    return {
        "base": base_dirs[graphenv],
        "data": os.path.join(base_dirs[graphenv], "data.json"),
        "graph": os.path.join(base_dirs[graphenv], "graph.json"),
    }


def create_name_mapping(name_groups: dict) -> dict:
    """
    Input: {"John": ["Johnny", "Jon"]}
    Output: {"John": "John", "Johnny": "John", "Jon": "John"}
    """
    mapping = {}
    for standard, variants in name_groups.items():
        mapping[standard.lower()] = standard.lower()  # Standard name maps to itself
        for variant in variants:
            mapping[variant.lower()] = standard.lower()
    return mapping


def _extract_character_pair(
    relation: dict, name_mapping: dict
) -> Optional[tuple[str, str]]:
    """Extract a pair of characters from a relation if valid"""
    if "character_mapping" not in relation:
        logger.debug("Relation missing character_mapping field")
        return None

    char_mapping = relation["character_mapping"]
    if len(char_mapping) != 2:
        logger.debug(f"Invalid number of characters in mapping: {len(char_mapping)}")
        return None

    from_char = next(iter(char_mapping[0].values()), None)
    to_char = next(iter(char_mapping[1].values()), None)

    if not isinstance(from_char, str) or not isinstance(to_char, str):
        logger.debug("Character values must be strings")
        return None

    from_char_mapped = name_mapping.get(from_char.lower())
    to_char_mapped = name_mapping.get(to_char.lower())

    if from_char_mapped and to_char_mapped:
        return (from_char_mapped, to_char_mapped)
    return None


def process_character_pairs(
    data: dict, name_mapping: dict
) -> tuple[Counter, list, int, int]:
    """Process relations to extract character pairs and counts"""
    character_counts = Counter()
    character_pairs = []
    total_relations = 0
    successful_relations = 0

    for chapter in data["relations"].values():
        for paragraph in chapter.values():
            for relation in paragraph:
                total_relations += 1
                char_pair = _extract_character_pair(relation, name_mapping)
                if char_pair:
                    successful_relations += 1
                    from_char, to_char = char_pair
                    character_counts.update([from_char, to_char])
                    character_pairs.append((from_char, to_char))

    return character_counts, character_pairs, total_relations, successful_relations


def create_nodes(character_counts: Counter) -> tuple[dict, list]:
    """Create node mapping and nodes list, excluding characters mentioned only once"""
    # Filter out characters with count = 1
    filtered_characters = {
        name: count for name, count in character_counts.items() if count > 1
    }

    # Log excluded characters
    excluded_characters = [
        name for name, count in character_counts.items() if count == 1
    ]
    if excluded_characters:
        logger.info(
            f"Excluding {len(excluded_characters)} characters that appear only once!"
        )

    node_mapping = {name: idx for idx, name in enumerate(filtered_characters.keys())}
    nodes = [
        {
            "id": idx,
            "name": name.lower(),
            "val": filtered_characters[name],
        }
        for name, idx in node_mapping.items()
    ]
    return node_mapping, nodes


def create_links(character_pairs: list, node_mapping: dict) -> tuple[list, set]:
    """
    Create links list with relationship counts, excluding single occurrences.
    Returns tuple of (links, connected_nodes)
    """
    relationship_counts = Counter(character_pairs)

    # Filter out relationships that only occur once
    filtered_relationships = {
        pair: count
        for pair, count in relationship_counts.items()
        if count > 1 and pair[0] in node_mapping and pair[1] in node_mapping
    }

    # Count dropped links
    dropped_links = len(relationship_counts) - len(filtered_relationships)
    logger.info(f"Dropped {dropped_links} links that only occurred once")

    # Keep track of nodes that have connections
    connected_nodes = set()
    for source, target in filtered_relationships.keys():
        connected_nodes.add(source)
        connected_nodes.add(target)

    links = [
        {"source": node_mapping[source], "target": node_mapping[target], "value": count}
        for (source, target), count in filtered_relationships.items()
    ]

    return links, connected_nodes


def create_character_list(data: dict, node_mapping: dict) -> list:
    """Create characters list with descriptions"""
    return [
        {
            "id": node_mapping[char.lower()],
            "name": char.lower(),
            "desc": desc,
        }
        for char, desc in data["characters"].items()
        if char.lower() in node_mapping
    ]


def create_character_relations(data: dict, node_mapping: dict) -> list:
    """Create character relations with IDs"""
    character_relations = []
    for relation in data["character_relations"]:
        from_name = relation["from"].lower()
        to_name = relation["to"].lower()

        if from_name not in node_mapping or to_name not in node_mapping:
            continue

        character_relations.append(
            {
                "from": from_name,
                "from_id": node_mapping[from_name],
                "to": to_name,
                "to_id": node_mapping[to_name],
                "description": relation["description"],
            }
        )
    return character_relations


def build_graph(data: dict) -> dict:
    """Build a graph from the JSON data"""
    name_mapping = create_name_mapping(data["name_groups"])

    # Process character pairs and get counts
    character_counts, character_pairs, total_relations, successful_relations = (
        process_character_pairs(data, name_mapping)
    )

    # Log processing statistics
    success_rate = (
        (successful_relations / total_relations * 100) if total_relations > 0 else 0
    )
    logger.info(f"Processed {total_relations} total relations")
    logger.info(f"Successfully extracted {successful_relations} character pairs")
    logger.info(f"Success rate: {success_rate:.2f}%")

    # Create graph components
    node_mapping, nodes = create_nodes(character_counts)
    links, connected_nodes = create_links(character_pairs, node_mapping)

    # Filter nodes to only include connected ones
    filtered_node_mapping = {
        name: idx for name, idx in node_mapping.items() if name in connected_nodes
    }
    filtered_nodes = [node for node in nodes if node["name"] in connected_nodes]

    characters = create_character_list(data, filtered_node_mapping)
    character_relations = create_character_relations(data, filtered_node_mapping)

    return {
        "nodes": filtered_nodes,
        "links": links,
        "characters": characters,
        "character_relations": character_relations,
    }


if __name__ == "__main__":
    if GRAPHENV not in ["karamazov", "solitude", "war_and_peace"]:
        sys.exit("Invalid environment. Use 'karamazov' or 'solitude'")

    paths = get_paths(GRAPHENV)
    data = read_json(paths["data"])
    graph = build_graph(data)
    write_json(paths["graph"], graph)
