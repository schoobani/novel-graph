relation_extraction_prompt = """
    The following is an excerpt from the novel _book_title_ :

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
    The following is an excerpt from the novel _book_title_ :

    _book_paragraph_

    Instructions:
    Character Identification: In the provided text, two characters— _character_A_ and _character_B_ —are mentioned. Identify them based on how their names commonly appear in the novel.

    1. **Name Correction**: For each character, retrieve their most commonly used full name throughout the novel. Pay special attention to whether they are referred to by middle names, abbreviations, or incomplete forms of their names, and ensure consistency with their full identity.  
    2. **Pronoun Replacement**: If any of these characters are referred to by pronouns such as he, she, or they, replace the pronoun with the correct full name of the character.  
    3. **Typographical Corrections**: Correct any spelling or typographical errors in the characters' names that may appear in the text.  
    4. **Familial Relationships**: If any relationships are mentioned such as "his child," "her father," or "his parents," identify the family member being referenced and replace the relationship term with the full name of the relevant character as they are identified in the book. Ensure that the relationship context is preserved.  
    5. **Do not use parentheses in any part of the output, including names.**  
    6. Do not use multiple names, map only to a single name per character.
    7. **Output Format**: Present the relationships between the mentioned characters and their correct full names in the following JSON structure. 
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

    "description" = {
        "description": "Character Description"
    }
"""

relation_description_prompt = """
    Context:
    You are analyzing the relationship between two characters, _character_A_ and _character_B_, in the novel _book_title_ . 
    Understanding their interactions, conflicts, and development within the story is crucial for literary analysis.

    High level relation points of the characters:
    _descriptions_

    Objective:
    Provide a concise yet insightful description of the dynamics between _character_A_ and _character_B_, maintaining the tone and style of the novel.

    Task Breakdown:

    - Summarize the nature of their relationship (e.g., friendship, rivalry, romance, mentorship).
    - Highlight key moments or developments that shape their interactions.
    - Capture any emotional, thematic, or symbolic elements tied to their relationship.
    - Maintain the tone and style of X to reflect the novel’s atmosphere.

    Additional Instructions:

    - Keep the response concise, limited to a single paragraph.
    - Focus only on key details without excessive elaboration.
    - If applicable, use language and style that match the novel’s tone.
    - Avoid extra information or unrelated content such as, here is youre description, etc.

    description: 
"""

name_group_prompt = """
    Context:
    You are given a list of character names from the novel _book_title_ . Some characters are known by multiple names, including aliases, nicknames, or alternate identities.

    Objective:
    Generate a structured JSON output that maps each character’s most commonly used name to a list of their other known names.

    Task Breakdown:

    Identify duplicates: Detect characters with multiple names and select the most commonly used name from the collection.

    Structure the output: Create a JSON dictionary where:
    The key is the character’s most frequently used (among provided options)
    The value is a list of their other known names (aliases, nicknames, alternate spellings) among provided options.
    Preserve exact spelling: Maintain the original spelling of all names as provided, without modifications, standardizations, or assumptions.
    Ensure valid JSON formatting: The final JSON must be syntactically correct and properly structured.
    Guidelines & Constraints:

    Follow a step-by-step approach to ensure all names from the list are processed.
    No duplicate mappings: Each character should appear as a key only once.
    Strict adherence to the provided list: Do not infer or generate names that are not explicitly given.
    Context-aware grouping: Use knowledge of _book_title_ to accurately associate names belonging to the same character.
    Identity-based grouping, not similarity-based: Do not group names based on resemblance but on actual character identity.

    Expected JSON Output:

    {
    "Full Name 1": ["Alias Name 1", "Alias Name 2", ...],
    "Full Name 2": ["Alias Name 3", "Alias Name 4", ...]
    }

    Here is the list of names:
    _character_names_
"""
