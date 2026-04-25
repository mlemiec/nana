import typer
import shlex
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel
from pathlib import Path

from nana.locale_manager import LocaleManager
from nana.setup_wizard import configure_environment, settings_menu
from nana import utils
from nana.request_handler import send_request_to_model
from nana.actions.housekeeping import tidy_vault
from nana.actions.extractor import extract_knowledge
from nana.actions.writer import finish_notes
from nana.actions.recipe import share_recipe
from nana.actions.tagger import assign_tag

console = Console(theme=utils.obsidian_theme)
lang = LocaleManager("en")
app = typer.Typer(help="Nana: Your personal knowledge assistant for Obsidian.")


def init():
    configure_environment(console)


def show_help():
    help_locale = lang.data.get("help", {})
    table = Table(
        title=help_locale.get("title", "Available Commands"),
        show_header=True,
        header_style="bold #BB86FC",
        border_style="#7B61FF",
        expand=False,
    )
    table.add_column("Command", style="bold #8BE9FD", no_wrap=True)
    table.add_column("Usage", style="#6272A4", no_wrap=True)
    table.add_column("Description", style="#89B4FA")

    rows = [
        ("clean",      "clean [path]",            help_locale.get("clean", "")),
        ("extract",    "extract",                  help_locale.get("extract", "")),
        ("finish",     "finish [path]",            help_locale.get("finish", "")),
        ("tag",        'tag "<path>" <tag>',       help_locale.get("tag", "")),
        ("recipe",     "recipe",                   help_locale.get("recipe", "")),
        ("call_model", "call_model <prompt>",      help_locale.get("call_model", "")),
        ("settings",   "settings",                 help_locale.get("settings", "")),
        ("help",       "help",                     help_locale.get("help", "")),
        ("exit",       "exit",                     help_locale.get("exit", "")),
    ]
    for cmd, usage, desc in rows:
        table.add_row(cmd, usage, desc)

    console.print(table)


@app.command()
def clean(
    path: str = typer.Option(None, help="Specific path to clean up"),
    dry_run: bool = typer.Option(False, help="Show what would be done without making changes")
):
    """Tidy up the /raw directory or a specific path."""
    config = utils.load_config()
    vault_path = Path(config.get("vault_path"))
    if dry_run:
        console.print(f"[warning]{lang.data.get('actions', {}).get('cleaning_dry_run', 'DRY RUN')}[/warning]")
    else:
        target_dir = Path(path) if path else None
        tidy_vault(vault_path, config, lang.data.get("actions", {}), target_dir=target_dir)


@app.command()
def extract():
    """Process new clippings from the /raw folder."""
    config = utils.load_config()
    vault_path = Path(config.get("vault_path"))
    extract_knowledge(vault_path, config, lang.data.get("actions", {}))


@app.command()
def finish(path: str = typer.Option(None, help="Specific file or directory to finish")):
    """Help finish incomplete notes in the vault or a specific path."""
    config = utils.load_config()
    vault_path = Path(config.get("vault_path"))
    target_path = Path(path) if path else None
    finish_notes(vault_path, config, lang.data.get("actions", {}), target_path=target_path)


@app.command()
def recipe():
    """Ask Nana for a secret recipe."""
    config = utils.load_config()
    share_recipe(config, lang.data.get("actions", {}))


@app.command()
def settings():
    """Interactively update vault path, API key, or model."""
    settings_menu(console, lang)


@app.command()
def tag(
    path: str = typer.Argument(..., help="Specific file or directory to tag"),
    tag_name: str = typer.Argument(..., help="The tag to add, e.g. '#incomplete'")
):
    """Add a specific tag to all markdown files in a path if missing."""
    config = utils.load_config()
    target_path = Path(path)
    assign_tag(target_path, tag_name, lang.data.get("actions", {}))


@app.command()
def call_model(prompt: str = typer.Argument(..., help="Prompt to send to the AI model")):
    """Send a prompt directly to the AI model."""
    response = send_request_to_model(user_prompt=prompt)
    console.print(f"[info]{response}[/info]")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    init()
    if ctx.invoked_subcommand is not None:
        return

    utils.show_welcome(console, lang)

    history_file = os.path.expanduser("~/.nana_history")
    session = PromptSession(history=FileHistory(history_file))

    while True:
        try:
            user_input = session.prompt(">> ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[error]{lang.data.get('ui', {}).get('goodbye', 'Goodbye!')}[/error]")
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as e:
            console.print(f"[error]{lang.data.get('ui', {}).get('command_parse_error', 'Error: {error}').format(error=e)}[/error]")
            continue

        command = args[0]

        if command == "exit":
            console.print(f"[error]{lang.data.get('ui', {}).get('goodbye', 'Goodbye!')}[/error]")
            break
        elif command == "clean":
            if len(args) > 1:
                clean(path=args[1], dry_run=False)
            else:
                clean(dry_run=False)
        elif command == "extract":
            extract()
        elif command == "finish":
            if len(args) > 1:
                finish(path=args[1])
            else:
                finish()
        elif command == "recipe":
            recipe()
        elif command == "tag":
            if len(args) == 3:
                tag(path=args[1], tag_name=args[2])
            else:
                console.print('[error]Usage: tag "<path>" <tag_name>[/error]')
        elif command == "call_model":
            if len(args) > 1:
                prompt = " ".join(args[1:])
                response = send_request_to_model(user_prompt=prompt)
                console.print(f"[info]{response}[/info]")
            else:
                console.print("[error]Usage: call_model <prompt>[/error]")
        elif command == "settings":
            settings_menu(console, lang)
        elif command == "help":
            show_help()
        else:
            console.print(f"[error]{lang.data.get('ui', {}).get('unknown_command', 'Unknown: {command}').format(command=command)}[/error]")


if __name__ == "__main__":
    app()
