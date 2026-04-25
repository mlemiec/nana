<div align="center">

![Nana UI](nana/assets/nana-256.png)
# NANA - NAna Not AI 

**NANA is your assitant for writing better notes and managing your vault.**

[![Version](https://img.shields.io/badge/version-0.0.1-blueviolet?style=flat-square)](https://github.com/yourusername/nana)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-17%20passing-brightgreen?style=flat-square)](#testing)

> *"I don't cook dinner yet, but I'll help you organize your mind so you have more time to enjoy yours."* — **Nana**

</div>

---

## What is Nana?

Nana is not just another AI wrapper. She is your digital **Babcia** (Grandma). While you do the hard work of reading and thinking, Nana handles the tedious bookkeeping of your personal knowledge base.

She works on top of your **Obsidian vault** — respecting your existing structure, never modifying source material, and always compounding your knowledge over time.

### The Philosophy: LLM Wiki, Not RAG

Most AI tools treat your documents as a temporary search index. Nana treats your notes like a **persistent, compounding codebase.**

- **Compounding** — The more you add, the smarter the wiki becomes.
- **Sovereign** — Works locally or with any cloud provider via OpenRouter. Your data stays in your Markdown files.
- **Human-Centric** — Nana doesn't write your notes *for* you; she prepares the "ingredients" so you can cook the "meal."

---

## Features

| Command | Description |
|---|---|
| `clean [path]` | 🧹 Renames messy files (e.g. `Untitled_123.md`) intelligently based on their content |
| `extract` | 📚 Converts raw web clips from `/raw` into structured, interlinked pages in `/wiki` |
| `finish [path]` | ✍️ Finds notes tagged `#incomplete` and suggests conclusions or missing sections |
| `tag <path> <tag>` | 🏷️ Adds a tag to all markdown files in a folder that don't already have it |
| `recipe` | 🍲 Asks Nana for a secret recipe — she's been known to share pierogi |

---

## Installation

**Requirements:** Python 3.12+, an Obsidian vault, an [OpenRouter](https://openrouter.ai) API key.

### Recommended — `pipx` (no Python prefix ever needed)

```bash
pipx install nana-wiki
nana
```

### One-line installer

```bash
curl -sSL https://raw.githubusercontent.com/mlemiec/nana/main/install.sh | bash
```

### From source (dev)

```bash
git clone https://github.com/mlemiec/nana.git
cd nana
pip install -e .
nana
```

> **What is pipx?** It installs Python CLI tools into isolated environments and exposes them globally — like `npm install -g` but for Python. Install it with `brew install pipx` or `pip install pipx`.

---

## Configuration

Create a `.env` file in the project root (or run `python src/cli.py` to be guided through setup):

```bash
NANA_VAULT_PATH=/path/to/your/obsidian/vault
NANA_API_KEY=sk-or-v1-your-openrouter-key
NANA_MODEL_NAME=google/gemma-3-27b-it:free
```

Nana uses [OpenRouter](https://openrouter.ai) by default, giving you access to hundreds of models — including free tiers.

---

## Vault Structure

Nana expects two folders in your Obsidian vault:

```
YourVault/
├── raw/        ← Drop your web clips and PDFs here (Nana never modifies these)
└── wiki/       ← Nana builds your interlinked knowledge base here
    ├── index.md
    └── log.md
```

**Obsidian Web Clipper tip:** Set the default save folder to `raw/` in the clipper settings. Then run `nana clean` to rename and `nana extract` to process.

---

## Usage

### Interactive Shell
```bash
python src/cli.py
>> clean
>> extract
>> finish /path/to/specific/note.md
>> tag "/path/to/folder" #incomplete
>> recipe
>> exit
```

### Direct Commands
```bash
python src/cli.py clean --path /path/to/folder
python src/cli.py extract
python src/cli.py finish --path /path/to/note.md
python src/cli.py tag /path/to/folder "#incomplete"
python src/cli.py recipe
```

> **Tip:** Use ↑/↓ arrow keys in the interactive shell to cycle through command history.

---

## AGENT.md / AGENTS.md — Behavior Instructions

Nana reads a `AGENT.md` file from the project root and injects it as a system prompt into **every** model request. This means you can control Nana's personality, formatting rules, and vault conventions without touching any code.

Edit `AGENT.md` to customise how she processes your notes, what format she uses for wiki pages, and how she handles Obsidian wiki-links vs. citations.

---

## Multilingual

Nana speaks your language. Set the locale in `src/cli.py`:

```python
lang = LocaleManager("pl")  # or "en"
```

| Language | Code | Status |
|---|---|---|
| English | `en` | ✅ Complete |
| Polish | `pl` | ✅ Complete |
| Other | — | Contributions welcome! |

---

## Testing

```bash
.venv/bin/python -m pytest tests/ -v
```

```
17 passed in 0.36s
```

All AI model calls are mocked — tests run instantly with no API calls.

---

## Project Structure

```
nana/
├── src/
│   ├── actions/
│   │   ├── housekeeping.py   # clean command
│   │   ├── extractor.py      # extract command
│   │   ├── writer.py         # finish command
│   │   ├── tagger.py         # tag command
│   │   └── recipe.py         # recipe command
│   ├── locales/
│   │   ├── en.yaml
│   │   └── pl.yaml
│   ├── cli.py                # Entry point & interactive shell
│   ├── request_handler.py    # OpenRouter API + AGENT.md injection
│   ├── locale_manager.py
│   ├── setup_wizard.py
│   └── utils.py
├── tests/
│   ├── test_housekeeping.py
│   ├── test_tagger.py
│   └── test_writer.py
├── AGENT.md                 # Nana's instruction manual
├── pyproject.toml
└── .env                      # Your secrets (gitignored)
```

---

## Roadmap

- [ ] `nana index` — auto-generate and update `wiki/index.md`
- [ ] `nana lint` — audit the wiki for orphan pages and contradictions
- [ ] `nana chat` — multi-turn conversation grounded in your wiki
- [ ] Local model support via Ollama (Bielik, Llama 3)
- [ ] `es`, `de`, `uk` locale additions

---

## Contributing

Want to teach Nana a new language or a new skill? PRs are welcome!

1. Fork the repo
2. Add your locale file to `src/locales/<code>.yaml`
3. Run the test suite
4. Open a pull request with a clear description

---

<div align="center">

Made with 💜 and a lot of tea.

**v0.0.1** — *She's just getting started.*

</div>
