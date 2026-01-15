#!/bin/bash
# OAIT Setup Script
# This script sets up the OAIT development environment

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              OAIT - Observational AI Tutor                ║"
echo "║                    Setup Script                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for uv
echo -e "${YELLOW}[1/6] Checking for uv package manager...${NC}"
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo -e "${GREEN}✓ uv installed${NC}"
else
    echo -e "${GREEN}✓ uv already installed${NC}"
fi

# Ensure PATH includes uv
export PATH="$HOME/.local/bin:$PATH"

# Create virtual environment
echo ""
echo -e "${YELLOW}[2/6] Creating virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    uv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo ""
echo -e "${YELLOW}[3/6] Installing dependencies...${NC}"
uv pip install -r requirements.txt
uv pip install -e .
# Ensure WebSocket support is installed
uv pip install 'uvicorn[standard]' websockets
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Install soundfile (needed for audio file reading)
echo ""
echo -e "${YELLOW}[4/6] Installing soundfile and system dependencies...${NC}"
uv pip install soundfile
# Check for libsndfile (required by soundfile)
if ! ldconfig -p | grep -q libsndfile; then
    echo -e "${YELLOW}Note: libsndfile may need to be installed on your system${NC}"
    echo "  Ubuntu/Debian: sudo apt install libsndfile1"
    echo "  Fedora: sudo dnf install libsndfile"
    echo "  macOS: brew install libsndfile"
fi
echo -e "${GREEN}✓ Audio dependencies installed${NC}"

# Create directories
echo ""
echo -e "${YELLOW}[5/6] Creating required directories...${NC}"
mkdir -p memory logs
echo -e "${GREEN}✓ Directories created${NC}"

# Setup .env file
echo ""
echo -e "${YELLOW}[6/6] Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠ Created .env from .env.example${NC}"
        echo -e "${RED}  IMPORTANT: Edit .env and add your OPENROUTER_API_KEY${NC}"
    else
        echo -e "${RED}⚠ No .env.example found. Creating minimal .env...${NC}"
        cat > .env << 'EOF'
# OAIT Configuration
# REQUIRED: Get your API key from https://openrouter.ai/
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=google/gemini-3-pro-preview

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=7860

# Whisper STT (local)
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE=int8

# Database
SQLITE_DB_PATH=./memory/oait.db
EOF
        echo -e "${RED}  IMPORTANT: Edit .env and add your OPENROUTER_API_KEY${NC}"
    fi
else
    # Check if API key is set
    if grep -q "your_openrouter_api_key_here" .env 2>/dev/null; then
        echo -e "${RED}⚠ OPENROUTER_API_KEY not configured in .env${NC}"
        echo "  Get your API key from https://openrouter.ai/"
    else
        echo -e "${GREEN}✓ .env configured${NC}"
    fi
fi

# Download Whisper model (optional, happens on first run)
echo ""
echo -e "${YELLOW}Whisper Model Info:${NC}"
echo "  The Whisper 'base' model (~150MB) will be downloaded on first run."
echo "  Models are cached in ~/.cache/huggingface/hub/"
echo ""
echo "  Available models:"
echo "    - base: ~150MB, fastest, good for English"
echo "    - small: ~500MB, better accuracy"
echo "    - medium: ~1.5GB, even better accuracy"
echo "    - large: ~3GB, best accuracy (requires GPU)"
echo ""

# Run tests
echo -e "${YELLOW}Running tests to verify setup...${NC}"
if python -m pytest tests/ -v --tb=short 2>/dev/null; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${YELLOW}⚠ Some tests may have failed - check output above${NC}"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Ensure your OPENROUTER_API_KEY is set in .env"
echo "  2. Activate the virtual environment:"
echo "       source .venv/bin/activate"
echo "  3. Start the server:"
echo "       python start_server.py"
echo "  4. Open http://localhost:7860 in your browser"
echo ""
echo "For development:"
echo "  - Run tests: pytest -v"
echo "  - Check errors: python -m pytest tests/ -v"
echo ""
