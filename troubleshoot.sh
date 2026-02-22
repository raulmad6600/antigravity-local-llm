#!/bin/bash

# Troubleshooting script para Antigravity Local LLM

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Troubleshooting Antigravity Local LLM${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

# 1. Check if API is running
echo -e "${YELLOW}1. Checking API Server...${NC}"
if curl -s http://localhost:8000/health | grep -q "status"; then
    echo -e "${GREEN}✅ API Server is running${NC}"
else
    echo -e "${RED}❌ API Server is NOT responding${NC}"
    echo "   Start with: source venv/bin/activate && python3 run.py"
fi

# 2. Check API port
echo -e "\n${YELLOW}2. Checking API Port (8000)...${NC}"
if lsof -i :8000 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Port 8000 is listening${NC}"
else
    echo -e "${RED}❌ Port 8000 is NOT listening${NC}"
fi

# 3. Check Ollama
echo -e "\n${YELLOW}3. Checking Ollama Server...${NC}"
if curl -s http://localhost:11434/api/tags | grep -q "models"; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
    echo "   Available models:"
    curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; data=json.load(sys.stdin); print('   ' + '\n   '.join([m['name'] for m in data.get('models', [])]))"
else
    echo -e "${RED}❌ Ollama is NOT responding (http://localhost:11434)${NC}"
    echo "   Start with: ollama serve"
fi

# 4. Check if llama3 model exists
echo -e "\n${YELLOW}4. Checking for llama3 model...${NC}"
if curl -s http://localhost:11434/api/tags 2>/dev/null | grep -q "llama3"; then
    echo -e "${GREEN}✅ llama3 model is available${NC}"
else
    echo -e "${YELLOW}⚠️  llama3 not found${NC}"
    echo "   Pull with: ollama pull llama3"
fi

# 5. Test Ollama directly
echo -e "\n${YELLOW}5. Testing Ollama API directly...${NC}"
OLLAMA_RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3", "prompt": "Say hello", "stream": false}' \
  -m 30)

if echo "$OLLAMA_RESPONSE" | grep -q "response"; then
    echo -e "${GREEN}✅ Ollama is responding correctly${NC}"
    echo "   Response sample:"
    echo "$OLLAMA_RESPONSE" | python3 -m json.tool | head -10
else
    echo -e "${RED}❌ Ollama is not responding to prompts${NC}"
    echo "   Response was:"
    echo "$OLLAMA_RESPONSE" | head -5
fi

# 6. Test API /health endpoint
echo -e "\n${YELLOW}6. Testing API Health Endpoint...${NC}"
HEALTH=$(curl -s http://localhost:8000/health)
echo -e "${GREEN}✅ Health response:${NC}"
echo "$HEALTH" | python3 -m json.tool | head -10

# 7. Test /v1/models endpoint
echo -e "\n${YELLOW}7. Testing /v1/models Endpoint...${NC}"
curl -s http://localhost:8000/v1/models | python3 -m json.tool

# 8. Test chat completion (without streaming)
echo -e "\n${YELLOW}8. Testing /v1/chat/completions Endpoint...${NC}"
echo "   Sending: 'Say hello in Spanish'"
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [
      {"role": "user", "content": "Say hello in Spanish"}
    ]
  }' \
  -m 60)

echo "$CHAT_RESPONSE" | python3 -m json.tool

# 9. Check logs
echo -e "\n${YELLOW}9. Latest API Logs (last 20 lines)...${NC}"
if [ -f "api.log" ]; then
    tail -20 api.log
else
    echo "   No api.log found"
fi

# 10. Summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Troubleshooting Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "If you're getting ${YELLOW}'no response'${NC} errors:"
echo -e "  1. Check if Ollama is running: ${BLUE}ollama serve${NC}"
echo -e "  2. Check if model exists: ${BLUE}ollama pull llama3${NC}"
echo -e "  3. Check API logs: ${BLUE}tail -f api.log${NC}"
echo -e "  4. Test Ollama directly: ${BLUE}curl -X POST http://localhost:11434/api/generate${NC}"
echo ""
echo -e "If API is not running:"
echo -e "  1. Activate venv: ${BLUE}source venv/bin/activate${NC}"
echo -e "  2. Start server: ${BLUE}python3 run.py${NC}"
echo ""
echo -e "For Continue in VS Code:"
echo -e "  1. Ensure config points to: ${BLUE}http://192.168.1.5:8000/v1${NC}"
echo -e "  2. Check Continue logs: ${BLUE}Cmd+Shift+P > Developer: Toggle Developer Tools${NC}"
