import os
from pathlib import Path
from openai import OpenAI
from nana.utils import load_config, NANA_CONFIG_DIR

config = load_config()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config.get("api_key"),
)


def get_agent_md_content():
    """Reads AGENT.md from the vault directory if it exists."""
    vault_path = config.get("vault_path")
    if vault_path:
        agent_md = Path(vault_path) / "AGENT.md"
        if agent_md.exists():
            return agent_md.read_text()
    # Fallback: ~/.nana/AGENT.md
    fallback = NANA_CONFIG_DIR / "AGENT.md"
    if fallback.exists():
        return fallback.read_text()
    return ""


def send_request_to_model(system_prompt=None, user_prompt=None, messages=None):
    """
    Sends a request to the model.
    You can either provide a system_prompt and user_prompt for a simple query,
    or provide a list of messages for a multi-turn conversation.
    """
    agent_rules = get_agent_md_content()

    if messages is None:
        messages = []

        combined_system_prompt = ""
        if agent_rules:
            combined_system_prompt += f"Here are the general project instructions and rules for the vault (from AGENT.md):\n\n{agent_rules}\n\n---\n\n"
        if system_prompt:
            combined_system_prompt += system_prompt

        if combined_system_prompt:
            messages.append({"role": "system", "content": combined_system_prompt.strip()})

        if user_prompt:
            messages.append({"role": "user", "content": user_prompt})
    else:
        if agent_rules:
            has_system = False
            for msg in messages:
                if msg.get("role") == "system":
                    msg["content"] = f"Here are the general project instructions and rules for the vault (from AGENT.md):\n\n{agent_rules}\n\n---\n\n{msg['content']}"
                    has_system = True
                    break
            if not has_system:
                messages.insert(0, {"role": "system", "content": f"Here are the general project instructions and rules for the vault (from AGENT.md):\n\n{agent_rules}"})

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