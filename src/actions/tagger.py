from pathlib import Path
from rich.console import Console

console = Console()

def assign_tag(target_path: Path, tag: str, locale: dict):
    if not target_path.exists():
        console.print(f"[error]{locale.get('path_not_found', 'Path not found.').format(path=target_path)}[/error]")
        return
        
    if not tag.startswith("#"):
        tag = f"#{tag}"
        
    console.print(f"[info]{locale.get('tag_start', 'Scanning...').format(path=target_path, tag=tag)}[/info]")
    
    files_to_check = []
    if target_path.is_file() and target_path.suffix == ".md":
        files_to_check = [target_path]
    elif target_path.is_dir():
        files_to_check = list(target_path.rglob("*.md"))
        
    if not files_to_check:
        console.print(f"[warning]{locale.get('tag_no_files', 'No markdown files found.')}[/warning]")
        return
        
    tagged_count = 0
    for file_path in files_to_check:
        try:
            content = file_path.read_text()
            if tag not in content:
                # Add tag to the bottom of the file
                new_content = content
                if not new_content.endswith("\n"):
                    new_content += "\n"
                new_content += f"\n{tag}\n"
                
                file_path.write_text(new_content)
                tagged_count += 1
                console.print(f"[success]{locale.get('tag_added', 'Tagged {filename}').format(tag=tag, filename=file_path.name)}[/success]")
        except Exception as e:
            console.print(f"[error]Failed to process {file_path.name}: {e}[/error]")
            
    console.print(f"[success]{locale.get('tag_done', 'Done! {count} files tagged.').format(tag=tag, count=tagged_count)}[/success]")
