QUICK START GUIDE
================

DEVELOPMENT (Local)
───────────────────

1. Set up environment:
   python3 -m venv venv
   source venv/bin/activate  # or: venv\Scripts\activate on Windows
   pip install -r requirements.txt

2. Start Ollama (in separate terminal):
   ollama serve

3. Run the API server:
   python run.py

4. Access the API:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health: http://localhost:8000/health

5. Test the endpoints:
   
   # Multi-agent query
   curl -X POST http://localhost:8000/v1/query \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Write a Python function that returns hello world"}'

   # OpenAI-compatible chat completion
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "local",
       "messages": [
         {"role": "user", "content": "Write a Python hello world function"}
       ]
     }'

TESTING
───────

Run all tests:
  pytest tests/ -v

Run specific test file:
  pytest tests/test_api.py -v

Run with coverage:
  pytest tests/ --cov=api --cov=core --cov-report=html

DEPLOYMENT (Production)
───────────────────────

1. One-command installation:
   bash install.sh

2. Remote deployment to macOS:
   bash install.sh --remote user@mac-mini.local

3. After installation:
   - API runs on http://0.0.0.0:8000
   - Systemd service: sudo systemctl status antigravity-local-llm
   - View logs: sudo journalctl -u antigravity-local-llm -f

VS CODE INTEGRATION
───────────────────

1. Install Continue extension in VS Code

2. Configure ~/.continue/config.json:
   {
     "models": [
       {
         "provider": "openai",
         "model": "local",
         "apiBase": "http://localhost:8000/v1",
         "completionOptions": {
           "maxTokens": 2000
         }
       }
     ]
   }

3. For remote access via SSH:
   ssh -L 8000:localhost:8000 user@mac-mini.local
   
   Then use: "apiBase": "http://localhost:8000/v1" in Continue config

KEY ENDPOINTS
─────────────

GET /health
  Returns: {"status": "ok", "version": "...", "app": "...", "debug": ...}

POST /v1/query
  Input: {"prompt": "...", "metadata": {...}}
  Output: {"id": "...", "result": {...}, "status": "success"}
  
POST /v1/chat/completions (OpenAI-compatible)
  Input: {
    "model": "local",
    "messages": [{"role": "user", "content": "..."}],
    ...
  }
  Output: {
    "id": "chatcmpl-...",
    "object": "chat.completion",
    "model": "local",
    "choices": [{
      "index": 0,
      "message": {"role": "assistant", "content": "..."},
      "finish_reason": "stop"
    }]
  }

POST /run (Legacy)
  Input: {"prompt": "..."}
  Output: {"plan": "...", "implementation": "...", "review": "..."}

CONFIGURATION
──────────────

Edit .env to configure:
  DEBUG=True|False
  LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
  OLLAMA_BASE_URL=http://localhost:11434
  OLLAMA_MODEL=llama3  # or any other Ollama model
  HOST=0.0.0.0
  PORT=8000
  MAX_ITERATIONS=3

TROUBLESHOOTING
────────────────

API won't start:
  - Check Ollama is running: ollama serve
  - Check port not in use: lsof -i :8000
  - Check logs: python run.py (will show errors)

Health check fails:
  - API must be running: python run.py
  - Wait 2-3 seconds for startup

Chat completions returns error:
  - Verify Ollama is reachable: curl http://localhost:11434/api/tags
  - Check model exists: ollama list
  - Pull model if needed: ollama pull llama3

Tests fail:
  - Install test dependencies: pip install -r requirements.txt
  - Run from project root: pytest tests/test_api.py -v

USEFUL COMMANDS
────────────────

# View API logs (development)
tail -f api.log

# View system service logs (production)
sudo journalctl -u antigravity-local-llm -f

# Stop API (development)
pkill -f "python.*run.py"

# Restart service (production)
sudo systemctl restart antigravity-local-llm

# Check Ollama models
ollama list

# Pull a new model
ollama pull mistral

# Clear cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Run in debug/watch mode
DEBUG=True python run.py

# Run specific port
PORT=9000 python run.py
