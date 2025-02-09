relation_extraction_prompt = (
    f"""
        The following is an excerpt from the novel _book_title_:

        _book_paragraph_

        Instructions:
        1. Character Extraction: Identify and extract all human characters or persons mentioned in the paragraph. Do not include places, objects, or abstract entities.
        2. Relationship Identification: For each pair of characters, determine the nature of their relationship based on the text. Relationships can include:

        Family ties (e.g., parent, child, sibling)
        Friendships
        Romantic connections
        Other relationships explicitly or implicitly stated in the paragraph.

        3. Output Format: Provide the relationships in the following JSON structure:
        """
    + """
        \n{
            "relations": [
                {
                "from": "Character A",
                "to": "Character B",
                "label": "relationship type",
                "description": "Brief quote or context from the text supporting the relationship"
                },
                {
                "from": "Character B",
                "to": "Character C",
                "label": "relationship type",
                "description": "Brief quote or context from the text supporting the relationship"
                },
                ...
            ]
        }
        """
    + """
        \n
        "from" and "to": Represent the two characters involved in the relationship.
        "label": The type of relationship (e.g., "parent", "friend", "spouse", etc.).
        "description": A short context or quote from the paragraph that justifies or illustrates the relationship.
        
        Key Requirements:

        Capture all relationships mentioned or implied in the text.
        Ensure that each relationship is unique and precise based on the paragraph.
        Do not infer relationships beyond what is provided in the paragraph.
        """
)
