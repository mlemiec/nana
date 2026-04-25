import re
from pathlib import Path
from datetime import datetime
from nana.request_handler import send_request_to_model
from rich.console import Console

console = Console()


def extract_knowledge(vault_path: Path, config: dict, locale: dict):
    raw_dir = vault_path / "raw"
    wiki_dir = vault_path / "wiki"

    wiki_dir.mkdir(parents=True, exist_ok=True)

    console.print(locale.get('extract_start', 'Scanning...'))

    if not raw_dir.exists():
        console.print(f"[error]{locale.get('raw_folder_not_found', 'raw/ not found.')}[/error]")
        return

    raw_files = list(raw_dir.glob("*.md"))

    if not raw_files:
        console.print(f"[info]{locale.get('extract_no_files', 'No clippings found.')}[/info]")
        return

    for file_path in raw_files:
        content = file_path.read_text()

        system_prompt = """You are Nana, the Librarian. Your job is to convert a raw clipping into a structured Wiki page.
Follow this format exactly:

# Page Title
**Summary**: One to two sentences describing this page.

**Sources**: [Raw file name]

**Last updated**: [Today's date]

---

Main content goes here. Use clear headings and short paragraphs.
Link to related concepts using [[wiki-links]] throughout the text.

## Related pages
- [[related-concept]]

Return ONLY the Markdown content for the new Wiki page. The first line should be the '# Page Title'."""

        response = send_request_to_model(
            system_prompt=system_prompt,
            user_prompt=f"Raw clipping filename: {file_path.name}\n\nContent:\n{content}"
        )

        lines = response.strip().split('\n')
        title_line = next((line for line in lines if line.startswith('# ')), "# Untitled")
        title = title_line.replace('# ', '').strip()

        filename_base = title.lower()
        filename_base = re.sub(r'[^a-z0-9\s-]', '', filename_base)
        filename_base = re.sub(r'[\s-]+', '-', filename_base).strip('-')
        if not filename_base:
            filename_base = "untitled-page"

        filename = f"{filename_base}.md"
        wiki_file_path = wiki_dir / filename
        wiki_file_path.write_text(response)

        console.print(f"[success]{locale.get('extract_wiki_created', 'Created: {filename}').format(filename=filename)}[/success]")

        log_path = wiki_dir / "log.md"
        today = datetime.now().strftime("%Y-%m-%d")
        log_entry = f"\n- {today}: Created [[{title}]] from {file_path.name}"
        if log_path.exists():
            with open(log_path, "a") as f:
                f.write(log_entry)
        else:
            log_path.write_text(f"# Wiki Log\n{log_entry}")

    console.print(f"[success]{locale.get('extract_done', 'Done!')}[/success]")
