#!/bin/bash
# Nana CLI Installer
# Usage: curl -sSL https://raw.githubusercontent.com/mlemiec/nana/main/install.sh | bash

set -e

GREEN='\033[0;32m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${PURPLE}👵 Installing Nana — NAna Not AI...${NC}"
echo ""

# Ensure pipx is available — install it if not
if ! command -v pipx &>/dev/null; then
    echo -e "${YELLOW}⚙️  pipx not found. Installing pipx first...${NC}"

    if command -v brew &>/dev/null; then
        brew install pipx
    elif command -v pip3 &>/dev/null; then
        pip3 install --user pipx
    elif command -v pip &>/dev/null; then
        pip install --user pipx
    else
        echo "❌ Could not find pip or brew to install pipx."
        echo "   Please install Python 3.12+ from https://python.org and try again."
        exit 1
    fi

    # Add pipx to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"

    # Ensure pipx is on PATH permanently
    python3 -m pipx ensurepath 2>/dev/null || pipx ensurepath 2>/dev/null || true
fi

echo "✅ Using pipx for a clean, isolated install."
pipx install nana-wiki --force

echo ""
echo -e "${GREEN}✅ Done! Nana is installed.${NC}"
echo ""
echo "  Run: nana"
echo ""
echo -e "${YELLOW}⚠️  If 'nana' is not found, restart your terminal or run:${NC}"
echo "     pipx ensurepath && source ~/.zshrc"
echo ""
