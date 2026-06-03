#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  王骁 x 小约翰可汗 Obsidian 笔记生成  ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

check_env() {
    if [ ! -f .env ]; then
        echo -e "${RED}ERROR: .env not found${NC}"
        echo "  cp .env.example .env"
        echo "  Edit .env and set DEEPSEEK_API_KEY"
        exit 1
    fi
    source .env
    if [ -z "${DEEPSEEK_API_KEY:-}" ] || [ "$DEEPSEEK_API_KEY" = "sk-your-key-here" ]; then
        echo -e "${RED}ERROR: DEEPSEEK_API_KEY not set in .env${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] .env configured${NC}"
}

check_python() {
    if [ ! -d .venv ]; then
        echo -e "${YELLOW}Creating virtualenv...${NC}"
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    pip install -q -r scripts/requirements.txt
    echo -e "${GREEN}[OK] Python deps installed${NC}"
}

step1_fetch() {
    echo ""
    echo -e "${YELLOW}[1/4] Fetching video lists from B站...${NC}"
    echo "  If you get '-352 风控校验失败', set a proxy:"
    echo "  export HTTP_PROXY=http://127.0.0.1:7890"
    echo ""
    python scripts/fetch_videos.py
}

step2_subtitles() {
    echo ""
    echo -e "${YELLOW}[2/4] Downloading subtitles...${NC}"
    python scripts/fetch_subtitles.py
}

step3_generate() {
    echo ""
    echo -e "${YELLOW}[3/4] Generating notes with DeepSeek V4...${NC}"
    echo "  This may take a while and consume API tokens."
    python scripts/generate_notes.py
}

step4_mocs() {
    echo ""
    echo -e "${YELLOW}[4/4] Building MOC indexes...${NC}"
    python scripts/build_mocs.py
}

summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Done!${NC}"
    echo ""
    echo "  Series directories:"
    for d in 01-奇葩小国 02-神奇组织 03-硬核狠人 04-骁话一下 05-王骁其他 06-小王看世界 00-主题索引; do
        count=$(find "$d" -name "*.md" ! -name ".gitkeep" 2>/dev/null | wc -l | tr -d ' ')
        echo "    $d: ${count:-0} notes"
    done
    echo ""
    echo "  Open this folder in Obsidian to browse."
    echo -e "${GREEN}========================================${NC}"
}

check_env
check_python
step1_fetch
step2_subtitles
step3_generate
step4_mocs
summary
