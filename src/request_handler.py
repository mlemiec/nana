import os
from pathlib import Path
from openai import OpenAI
from utils import load_config

config = load_config()
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=config.get("api_key"),
)

def get_claude_md_content():
    """Reads AGENT.md from the project root if it exists."""
    root_dir = Path(__file__).parent.parent
    claude_md_path = root_dir / "AGENT.md"
    if claude_md_path.exists():
        return claude_md_path.read_text()
    return ""

def send_request_to_model(system_prompt=None, user_prompt=None, messages=None):
    """
    Sends a request to the model.
    You can either provide a system_prompt and user_prompt for a simple query,
    or provide a list of messages for a multi-turn conversation.
    """
    claude_rules = get_claude_md_content()
    
    if messages is None:
        messages = []
        
        combined_system_prompt = ""
        if claude_rules:
            combined_system_prompt += f"Here are the general project instructions and rules for the vault (from AGENT.md):\n\n{claude_rules}\n\n---\n\n"
        if system_prompt:
            combined_system_prompt += system_prompt
            
        if combined_system_prompt:
            messages.append({"role": "system", "content": combined_system_prompt.strip()})
            
        if user_prompt:
            messages.append({"role": "user", "content": user_prompt})
    else:
        if claude_rules:
            has_system = False
            for msg in messages:
                if msg.get("role") == "system":
                    msg["content"] = f"Here are the general project instructions and rules for the vault (from AGENT.md):\n\n{claude_rules}\n\n---\n\n{msg['content']}"
                    has_system = True
                    break
            if not has_system:
                messages.insert(0, {"role": "system", "content": f"Here are the general project instructions and rules for the vault (from AGENT.md):\n\n{claude_rules}"})

    response = client.chat.completions.create(
      model=config.get("model_name"),
      messages=messages,
      extra_body={"reasoning": {"enabled": True}}
    )

    if not response or not response.choices:
        return "Oh dear, my mind went blank! The model didn't send anything back. Try again in a moment, sweetheart. 👵"

    content = response.choices[0].message.content
    if not content or not content.strip():
        return "Hmm, I started a thought but lost it halfway through... The model returned an empty response. Perhaps try a different question? 🤔"

    return content