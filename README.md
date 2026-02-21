# 🚀 Antigravity Local LLM: Multi-Agent AI Orchestration Engine

A production-ready FastAPI application implementing a multi-stage AI agent orchestration pipeline. Agents collaborate to analyze tasks, create implementation plans, develop code, and review results using local LLM models via Ollama.

**Current Version**: 1.0.0

---

## 📋 Table of Contents

1. [Architecture & Flow](#-architecture--flow)
2. [Prerequisites](#-prerequisites)
3. [Local Setup](#-local-setup)
4. [Running the Application](#-running-the-application)
5. [Deployment to Remote](#-deployment-to-remote)
6. [Production Operations](#-production-operations)
7. [API Reference](#-api-reference)
8. [Security](#-security)
9. [Troubleshooting](#-troubleshooting)
10. [Project Structure](#-project-structure)

---

## 🏗️ Architecture & Flow

Antigravity Local LLM implements a Planner → Coder → Reviewer agent pipeline:

```
User Task
    ↓
┌─────────────────────────────────────────────┐
│  PLANNER AGENT                              │
│  - Analyzes task requirements               │
│  - Creates technical implementation plan    │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│  CODER AGENT                                │
│  - Implements based on plan                 │
│  - Generates code/solution                  │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│  REVIEWER AGENT                             │
│  - Validates implementation                 │
│  - Quality assurance & testing              │
└──────────────┬──────────────────────────────┘
               ↓
         Pass/Fail?
        /          \
      PASS       FAIL (retry max 3 times)
      ↓              ↓
   Return         Restart
   Result         Pipeline
```

### Key Components

- **FastAPI**: High-performance Python web framework
- **Ollama**: Local LLM integration (llama3, llama3.1, etc.)
- **Pydantic**: Data validation and configuration management
- **Asyncio**: Non-blocking concurrent execution
- **Systemd**: Production service management (Linux)

### Agent Architecture

Each agent is:
- **Autonomous**: Can run independently or as part of pipeline
- **Stateless**: Results don't depend on execution order
- **Configurable**: Model and parameters adjustable via config
- **Observable**: Full execution logs and intermediate results

---

## 📦 Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu/Debian, RHEL/CentOS) or macOS
- **Python**: 3.9 or higher
- **Memory**: Minimum 4GB (8GB+ recommended for LLM)
- **Disk**: 20GB free (for Ollama models)

### External Services

- **Ollama v0.16+**: Local LLM server
  - Download: [ollama.ai](https://ollama.ai)
  - Default port: `11434`
  - Models: `llama3`, `llama3.1`, or compatible

### Software

```bash
# macOS (using Homebrew)
brew install python@3.11 git

# Ubuntu/Debian
sudo apt-get install python3.11 python3.11-venv git curl

# RHEL/CentOS
sudo yum install python3.11 git curl
```

---

## 🔧 Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/raulmad6600/antigravity-local-llm.git
cd antigravity-local-llm
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings (if needed)
nano .env
```

**Key .env Variables**:
```bash
DEBUG=True                              # Set to False in production
OLLAMA_BASE_URL=http://localhost:11434  # Ollama server URL
OLLAMA_MODEL=llama3                     # Default model
API_HOST=0.0.0.0                        # API bind address
API_PORT=8000                           # API port
MAX_ITERATIONS=3                        # Max agent retries
```

### 5. Start Ollama (Separate Terminal)

```bash
# macOS
ollama serve

# Linux (if installed as service)
systemctl start ollama
# or
ollama serve
```

### 6. Verify Installation

```bash
# Run mock tests (no Ollama required)
python tests/test_mock.py

# Verify configuration
python tests/verify.py
```

---

## ▶️ Running the Application

### Local Development

```bash
# Activate venv (if not already active)
source venv/bin/activate

# Start API server
python run.py
# or explicitly with uvicorn
uvicorn api.main:app --reload --port 8000 --host 0.0.0.0
```

**Server Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Health Check

```bash
# In another terminal
curl http://localhost:8000/health

# Expected response
{
  "status": "ok",
  "version": "1.0.0",
  "app": "Antigravity Local LLM",
  "debug": true
}
```

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🌐 Deployment to Remote

### One-Click Remote Deployment

Use the unified install script for automatic remote setup:

```bash
# Remote deployment (auto-detects and configures everything)
bash install.sh --remote user@your-remote-server.com:22
```

The script will automatically:
- Detect if it's a fresh install or update
- Clone or update repository
- Set up Python environment
- Install dependencies
- Start API with verification
- Run full test suite ✅
- Configure firewall ✅
- Setup systemd service ✅

### Manual Step-by-Step Deployment

#### Step 1: SSH into Remote Machine

```bash
ssh user@remote-server.com
```

#### Step 2: Clone Repository

```bash
cd ~
git clone https://github.com/raulmad6600/antigravity-local-llm.git
cd antigravity-local-llm
```

#### Step 3: Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Configure Environment

```bash
# Create .env from example
cp .env.example .env

# Edit for remote environment (change Ollama URL if needed)
nano .env
```

#### Step 5: Run Unified Installation Script

```bash
# Automated installation - Install, update, test, firewall, systemd
bash install.sh

# Deploy to remote
bash install.sh --remote user@your-server.com:22
```

The script automatically handles everything:
- Detects fresh install vs update
- Verifies Python and Git
- Creates virtual environment
- Installs dependencies
- Stops any running instances
- Starts API server
- **Runs all tests**
- **Configures firewall**
- **Sets up systemd service**

---

## 🛠️ Production Operations

### Unified Installation & Update Script

The `install.sh` script intelligently handles all operations automatically:

```bash
# Install or update (everything automated)
bash install.sh

# Deploy to remote machine
bash install.sh --remote user@your-server.com:22
```

**What The Script Always Does**:
1. Detects if fresh install or update
2. Verifies system (Python 3, Git)
3. Clones or updates repository
4. Creates/activates Python venv
5. Installs/upgrades dependencies
6. Stops any running API instances
7. Starts API server
8. Runs verification tests ✅
9. Configures firewall ✅
10. Sets up systemd service (Linux only) ✅
11. Displays status and summary

### Systemd Service Setup (Linux)

#### Automatic Setup

Use install script to automatically configure systemd:

```bash
bash install.sh --setup-service
```

This automatically:
- Copies service file to `/etc/systemd/system/`
- Updates paths based on your system
- Enables auto-start on boot
- Starts the service

#### Manual Setup

If you prefer manual setup:

```bash
# 1. Copy and edit service file
sudo cp config/antigravity-local-llm.service /etc/systemd/system/
sudo nano /etc/systemd/system/antigravity-local-llm.service

# 2. Edit these fields in the file:
# User=your-username
# WorkingDirectory=/path/to/antigravity-local-llm
# ExecStart=/path/to/antigravity-local-llm/venv/bin/python run.py

# 3. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable antigravity-local-llm
sudo systemctl start antigravity-local-llm
```

#### Service Commands

```bash
# Check status
sudo systemctl status antigravity-local-llm

# View logs
sudo journalctl -u antigravity-local-llm -f

# Restart
sudo systemctl restart antigravity-local-llm

# Stop
sudo systemctl stop antigravity-local-llm
```

### Firewall Configuration

#### Automatic Setup

```bash
# Automatically detect OS and configure firewall
bash install.sh --setup-firewall
```

Supports:
- UFW (Ubuntu/Debian)
- FirewallD (RHEL/CentOS)
- macOS (manual instructions)

#### Manual Setup by OS

**Ubuntu/Debian (UFW)**:
```bash
sudo ufw allow 8000/tcp   # FastAPI port
sudo ufw allow 11434/tcp  # Ollama port
sudo ufw allow 11434/udp
sudo ufw enable
```

**RHEL/CentOS (FirewallD)**:
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=11434/tcp
sudo firewall-cmd --permanent --add-port=11434/udp
sudo firewall-cmd --reload
```

**macOS**:
```bash
# System Preferences → Security & Privacy → Firewall
# Or disable: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
# Or allow incoming: pfctl -ef /etc/pf.conf (advanced)
```

### Monitoring

#### Health Endpoint

```bash
# Check API status
curl http://remote-server:8000/health

# Continuous monitoring
watch -n 5 'curl -s http://remote-server:8000/health | jq'
```

#### Process Status

```bash
# Check if API is running
ps aux | grep "python.*run.py"

# Check ports
lsof -i :8000  # API
lsof -i :11434 # Ollama
```

#### Logs

```bash
# If running in foreground
tail -f api.log

# If running as systemd service
sudo journalctl -u antigravity -f

# Errors only
grep ERROR api.log
```

---

## 📡 API Reference

### Health Check Endpoint

**GET** `/health`

Returns application status and version.

**Response** (200 OK):
```json
{
  "status": "ok",
  "version": "1.0.0",
  "app": "Antigravity Local LLM",
  "debug": true
}
```

### Run Task Endpoint

**POST** `/run`

Execute a task through the agent pipeline.

**Request Body**:
```json
{
  "task": "Write a Python function that validates email addresses",
  "language": "python",
  "context": "Enterprise application, must handle RFC 5322"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "result": "def validate_email(email: str) -> bool:\n    ...",
  "iterations": 2,
  "agent_outputs": {
    "planner": "Plan for email validation...",
    "coder": "Implementation code...",
    "reviewer": "Review passed: code is correct"
  }
}
```

**Response** (500 Error):
```json
{
  "status": "failed",
  "error": "Max iterations exceeded",
  "last_output": "Last reviewer feedback..."
}
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔐 Security

### Sensitive Files

**Never commit to git**:
- `.env` (local credentials)
- `*.key`, `*.pem` (private keys)
- `credentials.json`, `secrets.yaml`
- `.env.production`, `.env.staging`

These are automatically excluded by `.gitignore`.

### Pre-Commit Security Check

Before pushing to GitHub:

```bash
# Verify no .env files are staged
git status | grep -E "\.env|\.key|credentials"

# Remove accidentally staged files
git rm --cached .env
git rm --cached secrets/

# Verify clean history
git log --name-only -1
```

### Environment Variables

**For Remote Deployment**:

```bash
# Create .env on remote with local values
cat > ~/.env_production << EOF
DEBUG=False
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
MAX_ITERATIONS=3
EOF

# Reference in systemd service:
# EnvironmentFile=/home/smartlab/.env_production
```

### API Security Recommendations

1. **Authentication**: Add API key validation (future enhancement)
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Implement request throttling
4. **HTTPS**: Use reverse proxy (nginx) with SSL
5. **Input Validation**: All inputs validated via Pydantic models

---

## 🐛 Troubleshooting

### Port Already in Use

**Error**:
```
error: [Errno 48] Address already in use: ('0.0.0.0', 8000)
```

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python run.py --port 8001
```

### Ollama Connection Failed

**Error**:
```
Connection refused for http://localhost:11434
```

**Solutions**:
```bash
# 1. Verify Ollama is running
ps aux | grep ollama

# 2. Start Ollama
ollama serve

# 3. Check Ollama URL in .env
grep OLLAMA_BASE_URL .env

# 4. Test Ollama directly
curl http://localhost:11434/api/tags
```

### Model Not Found

**Error**:
```
{"error":"model 'llama3' not found"}
```

**Solution**:
```bash
# List available models
ollama list

# Pull required model
ollama pull llama3
ollama pull llama3.1  # Alternative

# Update .env
sed -i 's/OLLAMA_MODEL=.*/OLLAMA_MODEL=llama3.1/' .env
```

### High Memory Usage

**Symptoms**: API slows down, high RAM consumption

**Solutions**:
```bash
# Reduce model size (use smaller variant)
ollama pull tinyllama
sed -i 's/OLLAMA_MODEL=.*/OLLAMA_MODEL=tinyllama/' .env

# Limit max iterations
sed -i 's/MAX_ITERATIONS=.*/MAX_ITERATIONS=2/' .env

# Check memory
free -h        # Linux
vm_stat        # macOS
```

### Tests Failing

**Solution - Run Tests**:
```bash
# Mock tests (no Ollama required)
python tests/test_mock.py

# Verify configuration
python tests/verify.py

# Health check
curl http://localhost:8000/health

# Check logs
tail -50 api.log
```

### SSH Deployment Issues

**Too many authentication failures**:
```bash
# Wait 30 seconds and retry
sleep 30
bash install.sh --remote <USER>@<HOST>:<PORT>
```

**Connection timeout**:
```bash
# Verify remote is reachable
ping <REMOTE_HOST>

# Check SSH port
nmap -p 22 <REMOTE_HOST>

# Try with explicit timeout
ssh -o ConnectTimeout=10 user@host
```

---

## 📂 Project Structure

```
antrigravity-local-llm/
├── 📄 README.md                    # This file
├── 📄 VERSION                      # Current app version (1.0.0)
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Example environment variables
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 api/                         # FastAPI application
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Settings & configuration
│   ├── deps.py                    # Dependency injection
│   └── routes.py                  # API endpoints
│
├── 📁 core/                        # Core business logic
│   ├── __init__.py
│   ├── models.py                  # Pydantic data models
│   ├── agents/                    # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py               # BaseAgent abstract class
│   │   ├── planner.py            # Planner agent
│   │   ├── coder.py              # Coder agent
│   │   └── reviewer.py           # Reviewer agent
│   ├── llm/                       # LLM integration
│   │   ├── __init__.py
│   │   ├── base.py               # BaseLLM abstract class
│   │   └── ollama_adapter.py     # Ollama adapter
│   └── orchestrator/              # Agent orchestration
│       ├── __init__.py
│       └── engine.py             # Pipeline orchestrator
│
├── 📁 docs/                        # Documentation
│   └── OPERATIONS.md              # Production operations guide
│
├── 📁 tests/                       # Test suite
│   ├── test_mock.py               # Mock tests (no Ollama)
│   └── verify.py                  # Configuration verification
│
├── 📁 config/                      # Configuration files
│   └── antigravity.service        # Systemd service template
│
├── 📄 install.sh                  # Unified installation/update script
└── 📄 run.py                       # Application entry point
```

### Key Files Explained

| File | Purpose |
|------|---------|
| `run.py` | Entry point — starts Uvicorn server |
| `install.sh` | Unified installation/update/deployment script |
| `api/main.py` | FastAPI app creation and route registration |
| `api/config.py` | Pydantic settings management |
| `core/orchestrator/engine.py` | Multi-agent pipeline orchestration |
| `tests/test_mock.py` | Self-contained tests (no external deps) |
| `tests/verify.py` | Configuration and dependency checker |
| `VERSION` | Version number (read by app) |

---

## 📝 Versioning

### Current Version

```bash
cat VERSION
# Output: 1.0.0
```

### Checking Deployed Version

```bash
# Via health endpoint
curl http://localhost:8000/health | jq '.version'

# Via git
git describe --tags
```

### Updating Version

```bash
# 1. Update VERSION file
echo "1.1.0" > VERSION

# 2. Commit
git add VERSION
git commit -m "Release v1.1.0"

# 3. Tag (optional)
git tag v1.1.0

# 4. Push
git push origin main
git push origin --tags
```

---

## 🤝 Contributing

To contribute improvements:

1. Fork repository
2. Create feature branch: `git checkout -b feature/improvement`
3. Commit changes: `git commit -am 'Add improvement'`
4. Push branch: `git push origin feature/improvement`
5. Open Pull Request

---

## 📜 License

MIT License - See LICENSE file for details.

---

## 🆘 Support

### Resources

- **Documentation**: See `docs/` directory
- **Operations Guide**: `docs/OPERATIONS.md`
- **GitHub Issues**: Report bugs and request features
- **Code Examples**: Check `test_mock.py` for usage patterns

### Quick Start Commands

```bash
# Setup locally
git clone https://github.com/raulmad6600/antigravity-local-llm.git
cd antigravity-local-llm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python tests/test_mock.py

# Start server
python run.py

# Access API docs
open http://localhost:8000/docs
```

---

**Last Updated**: February 21, 2026  
**Version**: 1.0.0  
**Maintained by**: Antigravity Local LLM Team
