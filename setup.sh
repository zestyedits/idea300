#!/bin/bash

# Session Architect Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "======================================"
echo "  Session Architect Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env and add your OpenAI API key${NC}"
    echo -e "${YELLOW}  You can get an API key at: https://platform.openai.com/api-keys${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check if OpenAI API key is set
if grep -q "sk-your-api-key-here" .env 2>/dev/null; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  ACTION REQUIRED: Set your OpenAI API key${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "1. Get an API key: https://platform.openai.com/api-keys"
    echo "2. Open the .env file"
    echo "3. Replace 'sk-your-api-key-here' with your actual API key"
    echo ""
fi

# Generate secret key if needed
if grep -q "your-secret-key-here" .env 2>/dev/null; then
    echo ""
    echo "Generating Flask secret key..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # For macOS (BSD sed)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-secret-key-here-use-secrets-token-hex-32/$SECRET_KEY/" .env
    else
        # For Linux (GNU sed)
        sed -i "s/your-secret-key-here-use-secrets-token-hex-32/$SECRET_KEY/" .env
    fi
    
    echo -e "${GREEN}✓ Secret key generated${NC}"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p instance
echo -e "${GREEN}✓ Directories created${NC}"

# Success message
echo ""
echo -e "${GREEN}======================================"
echo "  Setup Complete!"
echo "======================================${NC}"
echo ""
echo "Next steps:"
echo "1. Make sure your OpenAI API key is set in .env"
echo "2. Run: source .venv/bin/activate"
echo "3. Run: python planner.py"
echo "4. Open: http://localhost:5000"
echo ""
echo -e "${YELLOW}Note: Don't forget to deactivate the virtual environment when done:${NC}"
echo "   deactivate"
echo ""