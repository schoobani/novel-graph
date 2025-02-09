relation_extraction_prompt = """
    The following is an excerpt from the novel _book_title_:

    _book_paragraph_

    Instructions:
    1. Character Extraction: Identify and extract all human characters or persons mentioned in the paragraph. Do not include places, objects, or abstract entities.
    2. Relationship Identification: For each pair of characters, determine the nature of their relationship based on the text. Relationships can include:

    Family ties (e.g., parent, child, sibling)
    Friendships
    Romantic connections
    Other relationships explicitly or implicitly stated in the paragraph.

    3. In case of using pronouns (e.g., he, she, they, his wife, her father, his father, etc...) to refer to characters, replace the pronouns with the correct full names of the characters.
    4. Output Format: Provide the relationships in the following JSON structure:
    \n
    {
        "relations": [
            {
            "from": "Character A",
            "to": "Character B",
            "label": "relationship type",
            "description": "quote or context from the text supporting the relationship"
            },
            {
            "from": "Character B",
            "to": "Character C",
            "label": "relationship type",
            "description": "quote or context from the text supporting the relationship"
            },
            ...
        ]
    }
    \n
    "from" and "to": Represent the two characters involved in the relationship.
    "label": The type of relationship (e.g., "parent", "friend", "spouse", etc.).
    "description": A short context or quote from the paragraph that justifies or illustrates the relationship.
    
    Key Requirements:

    Capture all relationships mentioned or implied in the text.
    Ensure that each relationship is unique and precise based on the paragraph.
    Do not infer relationships beyond what is provided in the paragraph.
    """


character_mapping_prompt = """
    The following is an excerpt from the novel _book_title_:

    _book_paragraph_

    Instructions:
    Character Identification: In the provided text, two characters— _character_A_ and _character_B_ —are mentioned. Identify them based on how their names commonly appear in the novel.

    1. Name Correction: For each character, retrieve their most commonly used full name throughout the novel. Pay special attention to whether they are referred to by middle names, abbreviations, or incomplete forms of their names, and ensure consistency with their full identity.
    2. Pronoun Replacement: If any of these characters are referred to by pronouns (e.g., he, she, they), replace the pronoun with the correct full name of the character.
    3. Typographical Corrections: Correct any spelling or typographical errors in the characters' names that may appear in the text.
    4. Familial Relationships: If any relationships are mentioned (e.g., "his child," "her father," "his parents"), identify the family member being referenced and replace the relationship term with the full name of the relevant character as they are identified in the book. Ensure that the relationship context is preserved.
    5. Output Format: Present the relationships between the mentioned characters and their correct full names in the following JSON structure:
    \n
    "relations": [
        {
            "_character_A_": "correct full names"
        },
        {
            "_character_B_": "Ocorrect full names"
        }
    ]
    """

character_description_prompt = """
    1. Introduction/Context
    You are tasked with generating a descriptive passage about a well-known literary character, ensuring that it aligns with the novel’s tone, setting, and themes.

    2. Objective
    Create a vivid, engaging, and well-structured paragraph that captures the essence of the character’s personality, physical appearance, and defining traits.

    3. Task Breakdown:
    Select the well-known character "_character_name_" from the famous novel: _book_title_
    Provide a rich, immersive description that highlights their physical features, demeanor, and personality.
    Ensure the portrayal is consistent with the novel’s tone, historical setting, and narrative style.
    Use evocative language to bring the character to life while maintaining conciseness and clarity.

    4. Additional Instructions:
    Avoid generic descriptions; instead, focus on distinctive qualities that define the character.
    Avoid generating extra information, be very concisce and only mention the character's traits as described in the novel.

    5. Output Format: Present the description of each character the following JSON structure:

    desc = {
        desc: "Character Description"
    }
"""
