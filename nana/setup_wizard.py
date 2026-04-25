import requests
from pathlib import Path
from dotenv import set_key, get_key
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from questionary import select

from nana import utils
from nana.locale_manager import LocaleManager
from nana.utils import NANA_CONFIG_DIR, NANA_ENV_PATH


FREE_MODELS_FALLBACK = [
    "google/gemma-3-27b-it:free",
    "minimax/minimax-m2.5:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-r1:free",
    "microsoft/phi-4-reasoning:free",
    "nvidia/llama-3.1-nemotron-70b-instruct:free",
    "qwen/qwen3-30b-a3b:free",
]


def fetch_free_models(api_key: str = None) -> list[str]:
    """Fetch the current list of free models from OpenRouter API."""
    try:
        headers = {"HTTP-Referer": "https://github.com/nana-cli"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            models = response.json().get("data", [])
            free_models = [
                m["id"] for m in models
                if str(m.get("pricing", {}).get("prompt", "1")) == "0"
                and str(m.get("pricing", {}).get("completion", "1")) == "0"
            ]
            return sorted(free_models) if free_models else FREE_MODELS_FALLBACK
    except Exception:
        pass
    return FREE_MODELS_FALLBACK


def settings_menu(console: Console, lang: LocaleManager):
    """Interactive settings menu to update vault path, API key, and model."""
    env_path = NANA_ENV_PATH
    current_vault = get_key(str(env_path), "NANA_VAULT_PATH") or "Not set"
    current_model = get_key(str(env_path), "NANA_MODEL_NAME") or "Not set"
    has_key = bool(get_key(str(env_path), "NANA_API_KEY"))

    table = Table(
        title="Current Settings",
        show_header=True,
        header_style="bold #BB86FC",
        border_style="#7B61FF",
        expand=False,
    )
    table.add_column("Setting", style="bold #8BE9FD", no_wrap=True)
    table.add_column("Value", style="#89B4FA")
    table.add_row("Vault Path", current_vault)
    table.add_row("API Key", "✅ Set" if has_key else "❌ Not set")
    table.add_row("Model", current_model)
    console.print(table)
    console.print()

    choices = [
        {"name": "📁  Change Vault Path", "value": "vault"},
        {"name": "🔑  Change API Key", "value": "api_key"},
        {"name": "🤖  Pick Model (fetches live free models)", "value": "model"},
        {"name": "↩️   Back", "value": "back"},
    ]

    action = select("What would you like to change?", choices=choices, style=None).ask()

    if action == "vault":
        try:
            new_vault = utils.folder_picker(
                lang.get("ui.utils.where_is_obsidian_vault"), console, lang
            )
            set_key(str(env_path), "NANA_VAULT_PATH", str(new_vault))
            console.print(f"[success]✅ Vault path updated to: {new_vault}[/success]")
        except ValueError:
            console.print("[warning]No folder selected, nothing changed.[/warning]")

    elif action == "api_key":
        new_key = Prompt.ask("Enter your OpenRouter API Key", password=True)
        if new_key.strip():
            set_key(str(env_path), "NANA_API_KEY", new_key.strip())
            console.print("[success]✅ API key updated.[/success]")
        else:
            console.print("[warning]No key entered, nothing changed.[/warning]")

    elif action == "model":
        console.print("[info]Fetching live free models from OpenRouter...[/info]")
        api_key = get_key(str(env_path), "NANA_API_KEY")
        free_models = fetch_free_models(api_key)
        console.print(f"[success]Found {len(free_models)} free models![/success]")

        chosen = select("Pick a model:", choices=free_models, style=None).ask()
        if chosen:
            set_key(str(env_path), "NANA_MODEL_NAME", chosen)
            console.print(f"[success]✅ Model updated to: {chosen}[/success]")


def setup_settings(console: Console, lang: LocaleManager):
    """Full first-time setup wizard."""
    NANA_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    console.print("[sub_header]Nana:[/sub_header] Calibration sequence initiated...")

    set_language(lang)

    try:
        vault_path = utils.folder_picker(
            lang.get("ui.utils.where_is_obsidian_vault"), console, lang
        )
    except ValueError:
        vault_path = str(Path.home())

    api_key = Prompt.ask("Please enter your OpenRouter API Key", password=True)

    console.print("[info]Fetching live free models from OpenRouter...[/info]")
    free_models = fetch_free_models(api_key)

    model_name = select("Pick a model:", choices=free_models, style=None).ask() or FREE_MODELS_FALLBACK[0]

    set_key(str(NANA_ENV_PATH), "NANA_VAULT_PATH", str(vault_path))
    set_key(str(NANA_ENV_PATH), "NANA_API_KEY", api_key)
    set_key(str(NANA_ENV_PATH), "NANA_MODEL_NAME", model_name)

    console.print("[success]Calibration complete! 👵✨[/success]")


def set_language(lang: LocaleManager):
    available_languages = ["en", "pl"]
    lang_code = select(
        f"{lang.get('ui.setup_wizard.language_selection')}",
        choices=available_languages,
        style=None
    ).ask()
    return LocaleManager(lang_code)


def configure_environment(console: Console):
    if not NANA_ENV_PATH.exists():
        lang = LocaleManager("en")
        setup_settings(console, lang)
