import os

from questionary import select
from rich.console import Console, RenderableType, Group
from pathlib import Path
from dotenv import load_dotenv
from rich.panel import Panel
from rich.text import Text

from rich_pixels import Pixels
from PIL import Image

from locale_manager import LocaleManager
from rich.theme import Theme

obsidian_theme = Theme({
    # Brand / Structural
    "vault": "bold #7B61FF",
    "header": "bold #d946ef",
    "sub_header": "bold #BB86FC", # Moved to lavender for hierarchy
    "border": "#7B61FF",

    # Functional / Data
    "path": "italic #6272A4",
    "selected_path": "bold #8BE9FD", # Use Cyan to indicate "Active"
    "tag": "#BB86FC",
    "link": "underline #8BE9FD",
    "info": "#89B4FA",             # Brighter blue for readability

    # Feedback Loop
    "success": "bold green",
    "warning": "bold #FFB74D",
    "error": "bold #FF5555",
    "danger": "white on #FF5555",
    "hint": "italic cyan",

    # User Input
    "prompt": "bold #BB86FC",
})

def get_config_path():
    # Store config in the user's home directory so it's global
    return Path.home() / ".nana_config"

def load_config():
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
            subfolders = [d for d in os.listdir(current_path) if not d.startswith('.') and os.path.isdir(os.path.join(current_path, d))]
        except PermissionError:
            console.print(f"[error]{lang.get('ui.errors.no_access_to_folder')}![/error]")
            subfolders = []

        choices = [
            {"name": f"✅ {lang.get('ui.utils.pick_folder')}", "value": "CONFIRM"},
            {"name": f"⬆️  .. {lang.get('ui.utils.up')}", "value": "UP"},
        ]

        for f in sorted(subfolders):
            choices.append({"name": f"📁 {f}", "value": f})

        answer = select(
            f"{lang.get('ui.utils.up')}",
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
            current_path = os.path.join(current_path, answer)

    return current_path

def show_welcome(console: Console, lang: LocaleManager):

    title_text = Text("NANA CLI", style="header")

    grandma_pixel = get_grandma_pixels()
    description_text = Text.from_markup(lang.get("ui.motto"))
    subtitle_text = Text.from_markup(lang.get("ui.welcome_subtitle"))

    welcome_content = create_welcome_grid(description_text, grandma_pixel)

    console.print(
        panel_styling(welcome_content, title_text, subtitle_text),
        justify="left" # This ensures the whole Panel stays on the left of the CLI
    )

def get_grandma_pixels():
    asset_path = "src/assets/nana.png"
    with Image.open(asset_path) as img:
        pixels = Pixels.from_image(img, resize=(24, 24))
    return pixels

def create_welcome_grid(body_text: Text, grandma_pixel: Pixels):
    return Group(
        grandma_pixel,
        "\n\n",
        body_text
    )

def panel_styling(content: RenderableType, title: Text, subtitle: Text = None):
    return Panel(
        content,
        title= title,
        subtitle= subtitle,
        title_align="left",
        border_style="border",
        expand=False,  # Shrinks the border to fit the content tightly
        padding=(1, 2),
    )