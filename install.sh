#!/bin/bash
# Nana CLI Installer
# Usage: curl -sSL https://raw.githubusercontent.com/mlemiec/nana/main/install.sh | bash

set -e

GREEN='\033[0;32m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo ""
echo -e "${PURPLE}👵 Installing Nana — NAna Not AI...${NC}"
echo ""

# Check if pipx is available
if command -v pipx &>/dev/null; then
    echo "✅ Found pipx — using it for a clean, isolated install."
    pipx install nana-wiki
    echo ""
    echo -e "${GREEN}✅ Done! Run 'nana' to get started.${NC}"
    exit 0
fi

# Fallback: check if pip is available
if command -v pip3 &>/dev/null; then
    echo "⚠️  pipx not found. Installing via pip3..."
    echo "   (Tip: 'pipx install nana-wiki' is the recommended way)"
    pip3 install nana-wiki
    echo ""
    echo -e "${GREEN}✅ Done! Run 'nana' to get started.${NC}"
    exit 0
fi

if command -v pip &>/dev/null; then
    echo "⚠️  pipx not found. Installing via pip..."
    pip install nana-wiki
    echo ""
    echo -e "${GREEN}✅ Done! Run 'nana' to get started.${NC}"
    exit 0
fi

echo "❌ Could not find pip or pipx."
echo ""
echo "Please install Python 3.12+ and then run:"
echo "  pip install pipx && pipx install nana-wiki"
exit 1
