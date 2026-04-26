# Release v0.0.5 — Initial Global Release

Nana is now a fully-fledged CLI tool that can be installed globally and used in any Obsidian vault.

## ✨ Highlights
- **Global Commands**: Use `nana` from any directory in your terminal.
- **Improved Installation**: Support for `pipx` and a one-liner install script.
- **Sovereign Configuration**: All settings are stored securely in `~/.nana/`.
- **Package Ready**: Properly structured as a Python package for distribution on PyPI.

## 🛠 Fixes & Improvements
- Added lazy-loading for the AI client to prevent crashes during setup.
- Standardized file paths for localized messages and assets.
- Integrated GitHub Actions for automated quality checks and publishing.

## 🚀 Getting Started
```bash
pipx install nana-wiki
nana
```
