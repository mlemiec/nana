from pathlib import Path
from nana.request_handler import send_request_to_model
from rich.console import Console

console = Console()


def tidy_vault(vault_path: Path, config: dict, locale: dict, target_dir: Path = None):
    raw_dir = target_dir if target_dir else vault_path / "raw"

    console.print(locale.get('cleaning_start', 'Scanning...'))

    messy_files = [f for f in raw_dir.rglob("*.md") if f.name.startswith(("Untitled", "web-clip"))]

    if not messy_files:
        console.print(locale.get('no_mess', 'All clean!'))
        return

    for file_path in messy_files:
        content = file_path.read_text()[:500]

        response = send_request_to_model(
            system_prompt="You are Nana. Suggest a short, clean filename (3-5 words) for this content. Use underscores. Return ONLY the filename.",
            user_prompt=content
        )

        new_name_slug = response.strip().replace(" ", "_")
        new_file_path = file_path.with_name(f"{new_name_slug}.md")

        file_path.rename(new_file_path)

        console.print(locale.get('cleaning_rename', '{old_name} -> {new_name}').format(
            old_name=file_path.name,
            new_name=new_file_path.name
        ))

    console.print(locale.get('cleaning_done', 'Done!'))