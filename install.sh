#!/bin/bash
#
# Antigravity Local LLM Unified Installation & Update Script
# Intelligently install or update based on machine state
# One-click install/update with verification
#
# Usage:
#   bash install.sh                          # Install/update + tests + firewall + systemd
#   bash install.sh --remote user@host:port  # Deploy to remote machine
#   bash install.sh --help                   # Show this help message
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
REPO_URL="https://github.com/raulmad6600/antigravity-local-llm.git"
PROJECT_NAME="antigravity-local-llm"
PROJECT_DIR="${PROJECT_DIR:-.}"
API_PORT=8000
OLLAMA_PORT=11434

# Flags
REMOTE_HOST=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --remote) REMOTE_HOST="$2"; shift 2 ;;
        --help|-h) 
            echo "Antigravity Local LLM Installation & Update Script"
            echo ""
            echo "Usage: bash install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --remote user@host:port   Deploy to remote machine"
            echo "  --help, -h               Show this help message"
            echo ""
            echo "The script ALWAYS performs:"
            echo "  ✓ Install or update based on system state"
            echo "  ✓ Setup Python environment"
            echo "  ✓ Run verification tests"
            echo "  ✓ Configure firewall"
            echo "  ✓ Setup systemd service (Linux only)"
            echo ""
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

print_header() {
    echo -e "\n${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} $1"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# ============================================================
# REMOTE DEPLOYMENT
# ============================================================

deploy_remote() {
    local host_spec="$1"
    local user=$(echo "$host_spec" | cut -d: -f1 | cut -d@ -f1)
    local host=$(echo "$host_spec" | cut -d@ -f2 | cut -d: -f1)
    
    # Extract port correctly - only if : exists in the full spec
    local port=22
    if echo "$host_spec" | grep -q ":"; then
        port=$(echo "$host_spec" | rev | cut -d: -f1 | rev)
    fi
    
    print_header "Remote Deployment to $user@$host:$port"
    
    log_info "Deploying to remote machine..."
    ssh -p "$port" "$user@$host" << 'REMOTE_EXEC'
#!/bin/bash
set -e

# Download and run install script locally on remote
if [ ! -d ~/antigravity-local-llm ]; then
    log_info "Cloning repository..."
    cd ~
    git clone https://github.com/raulmad6600/antigravity-local-llm.git
else
    log_info "Updating existing repository..."
    cd ~/antigravity-local-llm
    git pull origin main
fi

cd ~/antigravity-local-llm
bash install.sh $ARGS
REMOTE_EXEC

    log_success "Remote deployment complete!"
    exit 0
}

# ============================================================
# LOCAL INSTALLATION/UPDATE
# ============================================================

detect_installation_state() {
    print_section "Step 1/8: Detecting Installation State"
    
    if [ -d "$PROJECT_DIR/.git" ]; then
        INSTALLATION_STATE="UPDATE"
        log_success "Existing installation detected - will UPDATE"
    else
        INSTALLATION_STATE="INSTALL"
        log_success "Fresh installation detected - will INSTALL"
    fi
}

setup_repository() {
    if [ "$INSTALLATION_STATE" = "INSTALL" ]; then
        print_section "Step 2/8: Cloning Repository"
        log_info "Cloning from $REPO_URL..."
        git clone "$REPO_URL" "$PROJECT_DIR"
        cd "$PROJECT_DIR"
        log_success "Repository cloned successfully"
    else
        print_section "Step 2/8: Updating Repository"
        cd "$PROJECT_DIR"
        log_info "Fetching latest changes..."
        git fetch origin
        git pull origin main
        log_success "Repository updated to latest version"
    fi
}

verify_system() {
    print_section "Step 3/8: Verifying System Requirements"
    
    # Check Python
    if ! command -v python3 &>/dev/null; then
        log_error "Python 3 not found. Please install Python 3.9 or higher"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version)
    log_success "$PYTHON_VERSION available"
    
    # Check Git
    if ! command -v git &>/dev/null; then
        log_error "Git not found. Please install Git"
        exit 1
    fi
    log_success "Git available"
    
    # Check pip/venv
    if ! python3 -m pip --version &>/dev/null; then
        log_warning "pip not found, attempting to use apt/yum..."
        if command -v apt-get &>/dev/null; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif command -v yum &>/dev/null; then
            sudo yum install -y python3-pip
        fi
    fi
    log_success "All system requirements met"
}

setup_environment() {
    print_section "Step 4/8: Setting Up Python Environment"
    
    # Create venv if needed
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate venv
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --quiet --upgrade pip setuptools wheel
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install --quiet -r requirements.txt
    log_success "Dependencies installed successfully"
}

stop_running_api() {
    print_section "Step 5/8: Stopping Running Services"
    
    # Check if API is running
    if pgrep -f "python.*run.py" > /dev/null; then
        log_info "Found running API process, attempting graceful shutdown..."
        pkill -f "python.*run.py" || true
        sleep 2
        
        # Force kill if still running
        if pgrep -f "python.*run.py" > /dev/null; then
            log_warning "Forcing shutdown..."
            pkill -9 -f "python.*run.py" || true
        fi
        log_success "API stopped"
    else
        log_info "No running API process found"
    fi
    
    # Clear Python cache
    log_info "Clearing Python cache..."
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    log_success "Cache cleared"
}

start_api() {
    print_section "Step 6/8: Starting API Server"
    
    source venv/bin/activate
    
    # Ensure .env exists
    if [ ! -f .env ]; then
        log_info "Creating .env file from .env.example..."
        cp .env.example .env 2>/dev/null || echo "PORT=8000" > .env
        log_success ".env created"
    fi
    
    # Check if port 8000 is already in use
    local port=8000
    local port_process=$(lsof -ti:$port 2>/dev/null | head -1 || true)
    
    if [ -n "$port_process" ]; then
        log_warning "Port $port is already in use (PID: $port_process)"
        
        # Check if it's our Python API process
        if ps -p "$port_process" -o command= 2>/dev/null | grep -q "python.*run.py"; then
            log_info "Found old Python API process, stopping it..."
            kill -9 "$port_process" 2>/dev/null || true
            sleep 2
            log_success "Old API process stopped"
        else
            # It's a different process, find an available port
            local proc_info=$(ps -p "$port_process" -o comm= 2>/dev/null || echo "unknown")
            log_warning "Port 8000 is used by: $proc_info (not our API)"
            
            # Find next available port
            for try_port in 8001 8002 8003 8004 8005; do
                if ! lsof -ti:$try_port >/dev/null 2>&1; then
                    port=$try_port
                    log_info "Using alternative port $port instead"
                    
                    # Update .env with new port
                    if grep -q "^PORT=" .env; then
                        sed -i.bak "s/^PORT=.*/PORT=$try_port/" .env 2>/dev/null || \
                        sed -i "" "s/^PORT=.*/PORT=$try_port/" .env  # macOS compatible
                    else
                        echo "PORT=$try_port" >> .env
                    fi
                    log_success "Updated PORT to $port in .env"
                    break
                fi
            done
        fi
    fi
    
    log_info "Starting API server on port $port..."
    nohup python3 run.py > api.log 2>&1 &
    local api_pid=$!
    sleep 4
    
    # Verify it's running
    if pgrep -f "python.*run.py" > /dev/null; then
        log_success "API server started successfully on port $port"
        API_PORT=$port  # Update global API_PORT for later tests
    else
        log_error "Failed to start API server"
        tail -20 api.log
        exit 1
    fi
}

run_tests() {
    print_section "Step 7/8: Running Verification Tests"
    
    source venv/bin/activate
    
    # Test 1: Configuration verification
    log_info "Test 1/3: Configuration verification..."
    if python3 tests/verify.py > /dev/null 2>&1; then
        log_success "Configuration verification passed"
    else
        log_error "Configuration verification failed"
        exit 1
    fi
    
    # Test 2: Mock orchestrator test
    log_info "Test 2/3: Mock pipeline test..."
    if timeout 30 python3 tests/test_mock.py > /dev/null 2>&1; then
        log_success "Mock pipeline test passed"
    else
        log_error "Mock pipeline test failed"
        exit 1
    fi
    
    # Test 3: Health check
    log_info "Test 3/3: Health check endpoint..."
    for i in {1..10}; do
        if curl -s http://localhost:$API_PORT/health | grep -q "\"status\":\"ok\""; then
            log_success "Health check passed"
            curl -s http://localhost:$API_PORT/health | python3 -m json.tool | head -5
            break
        fi
        if [ $i -eq 10 ]; then
            log_error "Health check failed after 10 attempts"
            exit 1
        fi
        sleep 1
    done
}

configure_firewall() {
    print_section "Step 7.5/8: Configuring Firewall"
    
    if [ "$(uname -s)" = "Linux" ]; then
        if command -v ufw &>/dev/null; then
            log_info "Configuring UFW..."
            sudo ufw allow 22/tcp 2>/dev/null || true
            sudo ufw allow $API_PORT/tcp 2>/dev/null || true
            sudo ufw allow $OLLAMA_PORT/tcp 2>/dev/null || true
            sudo ufw allow $OLLAMA_PORT/udp 2>/dev/null || true
            log_success "UFW configured"
        elif command -v firewall-cmd &>/dev/null; then
            log_info "Configuring FirewallD..."
            sudo firewall-cmd --permanent --add-port=22/tcp 2>/dev/null || true
            sudo firewall-cmd --permanent --add-port=$API_PORT/tcp 2>/dev/null || true
            sudo firewall-cmd --permanent --add-port=$OLLAMA_PORT/tcp 2>/dev/null || true
            sudo firewall-cmd --permanent --add-port=$OLLAMA_PORT/udp 2>/dev/null || true
            sudo firewall-cmd --reload 2>/dev/null || true
            log_success "FirewallD configured"
        fi
    elif [ "$(uname -s)" = "Darwin" ]; then
        log_info "macOS detected - firewall configuration is manual"
        log_info "See README.md for macOS firewall instructions"
    fi
}

configure_systemd() {
    if [ "$(uname -s)" != "Linux" ]; then
        log_info "Systemd is Linux-only, skipping on $(uname -s)"
        return 0
    fi
    
    print_section "Step 7.6/8: Setting Up Systemd Service"
    
    SERVICE_FILE="/etc/systemd/system/antigravity-local-llm.service"
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    log_info "Installing systemd service..."
    sudo cp config/antigravity-local-llm.service "$SERVICE_FILE"
    
    # Update paths in service file
    sudo sed -i "s|/home/deploy|$HOME|g" "$SERVICE_FILE"
    sudo sed -i "s|antigravity-local-llm|$PROJECT_DIR|g" "$SERVICE_FILE"
    
    sudo systemctl daemon-reload
    sudo systemctl enable antigravity-local-llm
    sudo systemctl restart antigravity-local-llm
    
    log_success "Systemd service configured and started"
    sudo systemctl status antigravity-local-llm --no-pager
}

print_summary() {
    print_section "Step 8/8: Installation Complete"
    
    echo -e "${GREEN}✅ Antigravity Local LLM is ready!${NC}\n"
    
    # Get version
    VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
    
    # Get API status
    if curl -s http://localhost:$API_PORT/health | grep -q "status" 2>/dev/null; then
        API_STATUS="${GREEN}✅ Running${NC}"
    else
        API_STATUS="${RED}❌ Not responding${NC}"
    fi
    
    echo -e "${BLUE}📊 Status:${NC}"
    echo -e "   Application: Antigravity Local LLM"
    echo -e "   Version: $VERSION"
    echo -e "   API Status: $API_STATUS"
    echo -e "   API Port: $API_PORT"
    echo -e "   Ollama Port: $OLLAMA_PORT"
    echo ""
    
    echo -e "${BLUE}🔗 Access Points:${NC}"
    echo -e "   API: http://localhost:$API_PORT"
    echo -e "   Documentation: http://localhost:$API_PORT/docs"
    echo -e "   ReDoc: http://localhost:$API_PORT/redoc"
    echo ""
    
    echo -e "${BLUE}📝 Useful Commands:${NC}"
    echo -e "   View logs: tail -f api.log"
    echo -e "   Run tests: python tests/test_mock.py"
    echo -e "   Verify config: python tests/verify.py"
    echo -e "   Stop API: pkill -f 'python.*run.py'"
    echo ""
    
    if [ "$(uname -s)" = "Linux" ]; then
        echo -e "${BLUE}🔧 Linux Services:${NC}"
        echo -e "   Systemd status: sudo systemctl status antigravity-local-llm"
        echo -e "   View logs: sudo journalctl -u antigravity-local-llm -f"
    fi
    
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo -e "   README: README.md"
    echo -e "   Deployment: See README.md > Production Operations"
    echo ""
}

# ============================================================
# MAIN EXECUTION
# ============================================================

main() {
    print_header "Antigravity Local LLM Installation & Update Script"
    
    # Handle remote deployment
    if [ -n "$REMOTE_HOST" ]; then
        deploy_remote "$REMOTE_HOST"
        return
    fi
    
    # Local installation/update
    detect_installation_state
    setup_repository
    verify_system
    setup_environment
    stop_running_api
    start_api
    run_tests
    configure_firewall
    configure_systemd
    print_summary
    
    log_success "All steps completed successfully!"
}

main "$@"
