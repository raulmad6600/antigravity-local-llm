ARCHITECTURAL OVERVIEW
======================

SYSTEM ARCHITECTURE
───────────────────

┌─────────────────────────────────────────────────────────────────┐
│                      VS Code Continue                           │
│                    (OpenAI-Compatible Client)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP POST /v1/chat/completions
                         │ (OpenAI Format)
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    FastAPI Application                          │
│                  (api.main:app)                                 │
├─────────────────────────────────────────────────────────────────┤
│  Routes Layer (api/routes.py)                                  │
│  ├─ GET /health          → Health check                        │
│  ├─ POST /v1/query       → Multi-agent orchestration           │
│  ├─ POST /v1/chat/completions → OpenAI-compatible interface   │
│  └─ POST /run            → Legacy endpoint                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              Dependency Injection Layer (api/deps.py)           │
│         Singleton Orchestrator & LLM instances                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│            Core Orchestration System (core/)                    │
├─────────────────────────────────────────────────────────────────┤
│  Orchestrator Engine (core/orchestrator/engine.py)             │
│  ┌─────────────────────────────────────────────┐              │
│  │  Pipeline Flow:                             │              │
│  │  1. Task Input → Planner Agent             │              │
│  │  2. Plan → Coder Agent                      │              │
│  │  3. Implementation → Reviewer Agent        │              │
│  │  4. Review → PASS/FAIL Decision            │              │
│  │  5. Loop if FAIL (max_iterations)          │              │
│  │  6. Return results on PASS                 │              │
│  └─────────────────────────────────────────────┘              │
│                         ▼                                       │
│  Agent Layer (core/agents/)                                   │
│  ├─ BaseAgent (Abstract Base)                                 │
│  ├─ PlannerAgent → Creates development plan                  │
│  ├─ CoderAgent → Generates implementation                     │
│  └─ ReviewerAgent → Validates & improves code                │
│                         ▼                                       │
│  LLM Adapter Layer (core/llm/)                               │
│  ├─ BaseLLM (Abstract Interface)                             │
│  └─ OllamaAdapter (Async HTTP Client)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP POST /api/generate
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Ollama LLM Service                           │
│              (http://localhost:11434)                          │
│         (Runs locally - requires: ollama serve)               │
└─────────────────────────────────────────────────────────────────┘


DATA FLOW EXAMPLE
─────────────────

User Query: "Write a Python function that calculates factorial"

1. VS Code Continue Extension sends:
   POST /v1/chat/completions
   {
     "model": "local",
     "messages": [
       {"role": "user", "content": "Write a Python function that calculates factorial"}
     ]
   }

2. FastAPI routes.py → chat_completions() handler
   - Extracts user prompt
   - Creates Task object
   - Calls orchestrator.run()

3. Orchestrator Pipeline:
   
   ┌─────────────────────────────────────────┐
   │ STEP 1: Planner Agent                   │
   ├─────────────────────────────────────────┤
   │ Input: "Write a Python function..."     │
   │ System Prompt: Senior technical planner │
   │ → Calls OllamaAdapter.generate()        │
   │ Output: Structured development plan     │
   └─────────────────────────────────────────┘
                      ▼
   ┌─────────────────────────────────────────┐
   │ STEP 2: Coder Agent                     │
   ├─────────────────────────────────────────┤
   │ Input: Development plan from Step 1     │
   │ System Prompt: Senior software engineer │
   │ → Calls OllamaAdapter.generate()        │
   │ Output: Python implementation code      │
   └─────────────────────────────────────────┘
                      ▼
   ┌─────────────────────────────────────────┐
   │ STEP 3: Reviewer Agent                  │
   ├─────────────────────────────────────────┤
   │ Input: Implementation from Step 2       │
   │ System Prompt: Strict code reviewer     │
   │ → Calls OllamaAdapter.generate()        │
   │ Output: Review with PASS/FAIL decision  │
   └─────────────────────────────────────────┘
                      │
                      ├─ PASS: Return results
                      └─ FAIL: Loop back to Step 2 (if iterations < max)

4. Response returned to VS Code:
   {
     "id": "chatcmpl-...",
     "object": "chat.completion",
     "choices": [{
       "message": {
         "role": "assistant",
         "content": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"
       }
     }]
   }

5. VS Code displays the code suggestion


ASYNC EXECUTION FLOW
────────────────────

Entry Point: python run.py
         │
         └─ Loads config from .env
         │  └─ Binds to 0.0.0.0:8000
         │
         └─ Starts uvicorn ASGI server
            │
            └─ Listens for HTTP requests (async)
               │
               ├─ GET /health → health() coroutine
               ├─ POST /v1/query → query() coroutine
               ├─ POST /v1/chat/completions → chat_completions() coroutine
               │
               └─ Each request spawns async chain:
                  │
                  ├─ get_orchestrator() → Returns singleton
                  │  └─ Lazy initialization if needed
                  │
                  ├─ orchestrator.run() → async method
                  │  ├─ planner.run(context) → await async generate()
                  │  │  └─ OllamaAdapter.generate() → httpx.post() async
                  │  ├─ coder.run(context) → await async generate()
                  │  │  └─ OllamaAdapter.generate() → httpx.post() async
                  │  └─ reviewer.run(context) → await async generate()
                  │     └─ OllamaAdapter.generate() → httpx.post() async
                  │
                  └─ Response formatted & returned


MODULE DEPENDENCIES
───────────────────

Graph (No Circular Dependencies):

    api/main.py
        │
        ├─ api/routes.py
        │  ├─ api/deps.py
        │  │  ├─ core/llm/ollama_adapter.py
        │  │  │  └─ core/llm/base.py
        │  │  └─ core/orchestrator/engine.py
        │  │     ├─ core/agents/planner.py
        │  │     ├─ core/agents/coder.py
        │  │     ├─ core/agents/reviewer.py
        │  │     └─ core/agents/base.py
        │  │        └─ core/llm/ollama_adapter.py
        │  │
        │  ├─ api/schemas.py
        │  │  └─ pydantic
        │  │
        │  ├─ core/models.py
        │  │  └─ pydantic
        │  │
        │  └─ api/config.py
        │     └─ pydantic-settings
        │
        └─ api/config.py


CONFIGURATION HIERARCHY
───────────────────────

Environment (.env file)
    │
    └─ api/config.py (BaseSettings)
        │
        ├─ Field: debug (DEBUG env var)
        ├─ Field: log_level (LOG_LEVEL env var)
        ├─ Field: ollama_base_url (OLLAMA_BASE_URL env var)
        ├─ Field: ollama_model (OLLAMA_MODEL env var)
        ├─ Field: api_host (HOST env var, alias)
        ├─ Field: api_port (PORT env var, alias)
        └─ Field: max_iterations (MAX_ITERATIONS env var)
            │
            └─ Used by:
               ├─ run.py (server setup)
               ├─ api/routes.py (endpoints)
               └─ api/deps.py (orchestrator setup)


ERROR HANDLING CHAIN
────────────────────

API Request
    │
    ├─ Route handler (api/routes.py)
    │  ├─ Pydantic validation (schemas)
    │  │  └─ Invalid request → 422 Unprocessable Entity
    │  │
    │  └─ get_orchestrator() dependency
    │     └─ Orchestrator created (or returned from singleton)
    │        │
    │        ├─ orchestrator.run() async call
    │        │  │
    │        │  ├─ Planner: await llm.generate()
    │        │  │  └─ httpx.AsyncClient.post() 
    │        │  │     ├─ Timeout (120s) → TimeoutError
    │        │  │     ├─ Network error → httpx exception
    │        │  │     └─ response.raise_for_status() → HTTPStatusError
    │        │  │
    │        │  ├─ Coder: await llm.generate()
    │        │  │  └─ (same error handling)
    │        │  │
    │        │  └─ Reviewer: await llm.generate()
    │        │     └─ (same error handling)
    │        │
    │        └─ Returns result dict or error
    │
    └─ Response formatted and returned to client


PERFORMANCE CHARACTERISTICS
──────────────────────────

- Async I/O: Non-blocking operations throughout
- Singleton Pattern: Orchestrator and LLM created once, reused
- Connection Pooling: httpx.AsyncClient maintains connections
- Timeout Protection: 120s default on Ollama calls
- Memory: Minimal overhead (agents share LLM instance)
- Latency: ~3-20 seconds per query (depends on model)
- Throughput: Can handle multiple concurrent requests

Max Concurrent Requests: Limited by:
  - Uvicorn workers (default: auto-detect CPU count)
  - Ollama server capacity
  - System memory


TESTING ARCHITECTURE
────────────────────

tests/test_api.py
    │
    ├─ Fixtures:
    │  ├─ client (TestClient)
    │  └─ mock_orchestrator (AsyncMock)
    │
    ├─ Endpoint Tests:
    │  ├─ test_health_endpoint()
    │  ├─ test_v1_query_endpoint()
    │  ├─ test_v1_chat_completions_returns_valid_structure()
    │  └─ test_legacy_run_endpoint()
    │
    ├─ Request/Response Tests:
    │  ├─ test_chat_completions_with_multiple_messages()
    │  └─ test_v1_query_with_metadata()
    │
    ├─ Error Handling Tests:
    │  └─ test_chat_completions_no_user_message()
    │
    └─ Integration Tests:
       ├─ test_chat_completions_uses_implementation_as_fallback()
       └─ test_query_endpoint_includes_proper_id()

Mocking Strategy:
  - get_orchestrator dependency is patched
  - Orchestrator.run() returns mock data
  - No actual Ollama calls during testing
  - Tests run independently and fast


DEPLOYMENT TOPOLOGY
───────────────────

DEVELOPMENT (Local Machine)
  ┌──────────────────────────────┐
  │ MacBook Pro                  │
  ├──────────────────────────────┤
  │ Terminal 1: ollama serve     │
  │ (Ollama on :11434)           │
  │                              │
  │ Terminal 2: python run.py    │
  │ (API on :8000)               │
  │                              │
  │ Terminal 3: VS Code          │
  │ (Continue extension → :8000) │
  └──────────────────────────────┘


PRODUCTION (Remote Mac Mini)
  ┌──────────────────────────────┐
  │ Mac Mini                     │
  ├──────────────────────────────┤
  │ Ollama service running       │
  │ API service via systemd      │
  │ (Enabled on boot)            │
  │ Accessible via SSH           │
  └────────────┬─────────────────┘
               │
               │ SSH Tunnel
               │ (Local port 8000 → Remote port 8000)
               │
  ┌────────────▼──────────────┐
  │ MacBook Pro               │
  │ VS Code Continue          │
  │ Connect via localhost:8000│
  └───────────────────────────┘


KEY ACHIEVEMENTS
────────────────

✓ ASYNC-FIRST: All I/O operations are async
  - No blocking calls in hot paths
  - Multiple concurrent requests supported
  - Single threaded, efficient CPU usage

✓ MODULAR DESIGN: Clear separation of concerns
  - Easy to test each component
  - Easy to extend (add new agents)
  - Easy to replace (swap OllamaAdapter for OpenAI)

✓ PRODUCTION-READY: Enterprise best practices
  - Error handling throughout
  - Configuration management
  - Logging and monitoring
  - Systemd integration
  - Security (no secrets in code)

✓ OPENAI-COMPATIBLE: Works with existing tools
  - Continue extension support
  - Standard chat completion format
  - Easy to drop into workflows

✓ VS CODE INTEGRATION: Seamless workflow
  - Works locally or remotely via SSH
  - Natural code completion interface
  - Real-time suggestions from local LLM

END OF ARCHITECTURE OVERVIEW
