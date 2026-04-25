import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from request_handler import send_request_to_model
from rich.console import Console

console = Console()

def finish_notes(vault_path: Path, config: dict, locale: dict, target_path: Path = None):
    if target_path and target_path.is_file():
        files_to_check = [target_path]
    elif target_path and target_path.is_dir():
        files_to_check = target_path.rglob("*.md")
    else:
        # Default to entire vault
        files_to_check = vault_path.rglob("*.md")
        
    console.print(f"[info]{locale.get('finish_start', 'Looking for incomplete notes...')}[/info]")
    
    incomplete_files = []
    for f in files_to_check:
        try:
            content = f.read_text()
            if (target_path and target_path.is_file()) or "#incomplete" in content:
                incomplete_files.append((f, content))
        except Exception:
            pass
            
    if not incomplete_files:
        console.print(f"[info]{locale.get('finish_no_incomplete', 'No incomplete notes found.')}[/info]")
        return
        
    for file_path, content in incomplete_files:
        console.print(f"[info]{locale.get('finish_helping', 'Helping finish {filename}...').format(filename=file_path.name)}[/info]")
        
        system_prompt = """You are Nana, the Co-Writer. The user has an incomplete note that you must help finish.

IMPORTANT RULES:
- The NOTE TITLE / FILENAME tells you the REAL topic. Always focus on that specific topic.
- [[wiki-links]] like [[AI <Home node>]] are Obsidian navigation links, NOT the subject of the note. Completely ignore them when determining what the note is about.
- Read the existing text carefully for any partial content or hints, then continue from where the author left off.
- Provide ONLY the markdown content to be appended. Do not repeat existing content. Do not include the #incomplete tag.
- If adding a conclusion or summary, use a ## Conclusion heading.
- Write in a clear, educational, warm tone."""
        
        response = send_request_to_model(
            system_prompt=system_prompt,
            user_prompt=f"Note filename (this is the REAL topic): {file_path.stem}\n\nExisting content:\n{content}"
        )
        
        # We append the response to the note and remove the #incomplete tag
        new_content = content.replace("#incomplete", "")
        new_content += "\n\n" + response.strip() + "\n"
        
        file_path.write_text(new_content)
        console.print(f"[success]{locale.get('finish_done_file', 'Finished {filename}').format(filename=file_path.name)}[/success]")
        
    console.print(f"[success]{locale.get('finish_done_all', 'All done!')}[/success]")
