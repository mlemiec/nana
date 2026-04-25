import time
import typer
import shlex
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.prompt import Prompt
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel

from locale_manager import LocaleManager
from setup_wizard import configure_environment, settings_menu
import utils
from request_handler import send_request_to_model
from pathlib import Path

# Import actions
from actions.housekeeping import tidy_vault
from actions.extractor import extract_knowledge
from actions.writer import finish_notes
from actions.recipe import share_recipe
from actions.tagger import assign_tag

console = Console(theme=utils.obsidian_theme)

lang = LocaleManager("en")

app = typer.Typer(help="Nana: Your Grandam Wiki Assistant.")

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
        console.print("[warning]DRY RUN: No files were actually moved.[/warning]")
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
def call_model(prompt: str = typer.Argument(..., help="Prompt to send to Claude Code")):
    console.print(f"[info] Calling model via OpenRouter [/info]")
    response = send_request_to_model(user_prompt=prompt)
    console.print(f"[info]{response}[/info]")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    init()
    if ctx.invoked_subcommand is not None:
        return  # Let Typer handle the subcommand

    utils.show_welcome(console, lang)
    
    # Enable command history
    history_file = os.path.expanduser("~/.nana_history")
    session = PromptSession(history=FileHistory(history_file))

    while True:
        try:
            # We use a simple prompt string here, but rich handles the rest of the output
            user_input = session.prompt(">> ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[error]Goodbye![/error]")
            break
            
        if not user_input:
            continue
            
        try:
            args = shlex.split(user_input)
        except ValueError as e:
            console.print(f"[error]Error parsing command: {e}[/error]")
            continue
            
        command = args[0]
        
        if command == "exit":
            console.print("[error]Goodbye![/error]")
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
                console.print("[error]Usage: tag \"<path>\" <tag_name>[/error]")
        elif command == "call_model":
            if len(args) > 1:
                prompt = " ".join(args[1:])
                print(prompt)
                response = send_request_to_model(user_prompt=prompt)
                console.print(f"[info]{response}[/info]")
            else:
                console.print("[error]Usage: call_model <prompt>[/error]")
        elif command == "settings":
            settings_menu(console, lang)
        elif command == "help":
            show_help()
        else:
            console.print(f"[error]Sorry I don't understand that command: {command}[/error]")

if __name__ == "__main__":
    app()
