# Novel Graph  
A tool for extracting character interaction graphs from novels.  

## How is the Graph Built?  
This pipeline processes novels in chunks using OpenAI models to generate:  

- **Character relationships** – Identifies and maps all connections between characters.  
- **Character descriptions** – Provides summaries of each character.  
- **Interaction details** – Explains character interactions in depth.  

## How to Run  

1. Create and activate a virtual environment:  
   ```sh
   uv venv
   source .venv/bin/activate
   uv lock
   uv sync
   ```

2. Set your OpenAI API key:  
   ```sh
   export OPENAI_KEY='<your_api_key>'
   ```

3. Make the script executable:  
   ```sh
   chmod +x generate.sh
   ```

4. Generate the character graph for a novel:  
   ```sh
   ./generate.sh karamazov  # Or use: solitude, master-and-margarita, war-and-peace
   ```  

## Request a Novel  
Would you like to see a specific book visualized in the graph? Open an issue so I can pick it up or get your hands dirty and open a PR. 
