import sys
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

sys.path.append(str(Path(__file__).parent.parent))
from request_handler import send_request_to_model

console = Console()

def share_recipe(config: dict, locale: dict):
    console.print(f"[info]{locale.get('recipe_start', 'Looking through cookbooks...')}[/info]")
    
    system_prompt = """You are Nana, a sweet digital Grandma. The user asked for a secret recipe.
Share one of your favorite, comforting recipes (e.g. pierogi, apple pie, chicken soup, chocolate chip cookies).
Write it in a warm, loving tone. Include a short story about why it's special.
Output the recipe in Markdown format."""
    
    response = send_request_to_model(
        system_prompt=system_prompt,
        user_prompt="Nana, could you please share a secret recipe with me?"
    )
    
    console.print("\n")
    console.print(Markdown(response))
    console.print(f"\n[success]{locale.get('recipe_enjoy', 'Enjoy, dear! ✨👵')}[/success]")
