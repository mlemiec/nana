import os
from pathlib import Path
from dotenv import load_dotenv
from questionary import select
from rich.console import Console, RenderableType, Group
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich_pixels import Pixels
from PIL import Image

from nana.locale_manager import LocaleManager

# User config dir — works globally when installed
NANA_CONFIG_DIR = Path.home() / ".nana"
NANA_ENV_PATH = NANA_CONFIG_DIR / ".env"

obsidian_theme = Theme({
    # Brand / Structural
    "vault": "bold #7B61FF",
    "header": "bold #d946ef",
    "sub_header": "bold #BB86FC",
    "border": "#7B61FF",

    # Functional / Data
    "path": "italic #6272A4",
    "selected_path": "bold #8BE9FD",
    "tag": "#BB86FC",
    "link": "underline #8BE9FD",
    "info": "#89B4FA",

    # Feedback Loop
    "success": "bold green",
    "warning": "bold #FFB74D",
    "error": "bold #FF5555",
    "danger": "white on #FF5555",
    "hint": "italic cyan",

    # User Input
    "prompt": "bold #BB86FC",
})


def load_config():
    """Load config from ~/.nana/.env (global), fallback to local .env."""
    # Try global config first, then local
    if NANA_ENV_PATH.exists():
        load_dotenv(NANA_ENV_PATH)
    else:
        load_dotenv()
    return {
        "vault_path": os.getenv("NANA_VAULT_PATH"),
        "api_key": os.getenv("NANA_API_KEY"),
        "model_name": os.getenv("NANA_MODEL_NAME")
    }


def folder_picker(question: str, console: Console, lang: LocaleManager, start_path=".") -> str:
    current_path = os.path.abspath(start_path)
    console.print(question)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        path_text = Text.assemble(
            (f"{lang.get('ui.utils.path')}\n", "sub_header"),
            (current_path, "selected_path")
        )

        console.print(Panel.fit(path_text))

        try:
            subfolders = [
                f for f in os.scandir(current_path)
                if f.is_dir() and not f.name.startswith('.')
            ]
        except PermissionError:
            console.print("[error]No access to this folder.[/error]")
            current_path = str(Path(current_path).parent)
            continue

        choices = [
            {"name": f"✅ {lang.get('ui.utils.pick_folder')}", "value": "CONFIRM"},
            {"name": f"⬆️  .. {lang.get('ui.utils.up')}", "value": "UP"},
        ]

        for f in sorted(subfolders, key=lambda x: x.name.lower()):
            choices.append({"name": f"📁 {f.name}", "value": f.path})

        answer = select(
            lang.get("ui.utils.where_you_wanna_move"),
            choices=choices,
            style=None
        ).ask()

        if answer == "CONFIRM":
            break
        elif answer is None:
            raise ValueError("cancelled")
        elif answer == "UP":
            current_path = os.path.dirname(current_path)
        else:
            current_path = answer

    return current_path


def show_welcome(console: Console, lang: LocaleManager):
    assets_dir = Path(__file__).parent / "assets"
    pixel_art = ""
    try:
        img_path = assets_dir / "nana-256.png"
        if img_path.exists():
            img = Image.open(img_path).convert("RGBA").resize((14, 14))
            pixel_art = Pixels.from_image(img)
    except Exception:
        pass

    welcome_text = Text.from_markup(lang.get("ui.motto"))
    content = Group(pixel_art, welcome_text) if pixel_art else welcome_text

    console.print(
        Panel(
            content,
            title=f"[header]{lang.get('ui.welcome_title')}[/header]",
            subtitle=f"[hint]{lang.get('ui.welcome_subtitle')}[/hint]",
            border_style="vault",
            padding=(1, 2),
        )
    )