#!/bin/bash
# Sentinel Edge - Production Startup Script
# Usage: ./start.sh [--dev|--prod|--stop|--status]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="sentinel-edge"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-5000}"
WORKERS="${WORKERS:-4}"
THREADS="${THREADS:-2}"
LOG_FILE="logs/${APP_NAME}.log"
PID_FILE="${APP_NAME}.pid"

# Create logs directory
mkdir -p logs

# Function to print colored messages
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to check if port is in use
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    if check_port; then
        warn "Port $PORT is already in use"
        read -p "Kill existing process? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
            sleep 2            success "Killed process on port $PORT"
        else
            error "Cannot start server"
            exit 1
        fi
    fi
}

# Function to install dependencies
install_deps() {
    info "Checking dependencies..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        warn "Virtual environment not found. Creating..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    if ! pip show flask >/dev/null 2>&1; then
        info "Installing Python dependencies..."
        pip install -r requirements.txt --quiet
    fi
    
    # Install gunicorn if not present
    if ! command -v gunicorn &> /dev/null; then
        info "Installing gunicorn..."
        pip install gunicorn --quiet
    fi
    
    success "Dependencies ready"
}

# Function to start in development mode
start_dev() {
    info "Starting in DEVELOPMENT mode..."
    info "Server: http://$HOST:$PORT"
    info "Press CTRL+C to stop"
    echo
    
    kill_port
    
    # Use Flask development server
    export FLASK_APP=app.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1
        python -m flask run --host=$HOST --port=$PORT
}

# Function to start in production mode
start_prod() {
    info "Starting in PRODUCTION mode..."
    info "Server: http://$HOST:$PORT"
    info "Workers: $WORKERS | Threads: $THREADS"
    info "Logs: $LOG_FILE"
    info "PID: $PID_FILE"
    echo
    
    kill_port
    
    # Create log directory if not exists
    mkdir -p logs
    
    # Start gunicorn in background
    gunicorn \
        --name $APP_NAME \
        --workers $WORKERS \
        --threads $THREADS \
        --bind $HOST:$PORT \
        --access-logfile $LOG_FILE \
        --error-logfile $LOG_FILE \
        --log-level info \
        --pid $PID_FILE \
        --daemon \
        app:app
    
    sleep 2
    
    # Check if started successfully
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        success "Server started (PID: $PID)"
        success "Dashboard: http://$HOST:$PORT/dashboard"
        success "Health: http://$HOST:$PORT/health"
        echo
        info "To stop: ./start.sh --stop"
        info "To view logs: tail -f $LOG_FILE"
    else
        error "Failed to start server. Check $LOG_FILE"
        exit 1
    fi
}

# Function to stop server
stop_server() {
    info "Stopping server..."    
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            rm -f $PID_FILE
            success "Server stopped (PID: $PID)"
        else
            warn "Process $PID not running"
            rm -f $PID_FILE
        fi
    elif check_port; then
        warn "No PID file found, killing process on port $PORT"
        lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
        success "Killed process on port $PORT"
    else
        warn "Server is not running"
    fi
}

# Function to show status
show_status() {
    info "Checking server status..."
    
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if kill -0 $PID 2>/dev/null; then
            success "Server is running (PID: $PID)"
            echo
            info "Testing health endpoint..."
            if curl -s http://$HOST:$PORT/health | grep -q "online"; then
                success "Health check: PASSED"
            else
                warn "Health check: FAILED"
            fi
        else
            warn "PID file exists but process not running"
            rm -f $PID_FILE
        fi
    elif check_port; then
        warn "Port $PORT is in use but no PID file found"
        info "Server might be running in development mode"
    else
        info "Server is not running"
    fi
}

# Function to show help
show_help() {
    echo "Sentinel Edge - Production Startup Script"    echo
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  --dev       Start in development mode (Flask dev server)"
    echo "  --prod      Start in production mode (gunicorn) [DEFAULT]"
    echo "  --stop      Stop the server"
    echo "  --status    Show server status"
    echo "  --help      Show this help message"
    echo
    echo "Environment Variables:"
    echo "  HOST        Server host (default: 127.0.0.1)"
    echo "  PORT        Server port (default: 5000)"
    echo "  WORKERS     Gunicorn workers (default: 4)"
    echo "  THREADS     Gunicorn threads per worker (default: 2)"
    echo
    echo "Examples:"
    echo "  $0                    # Start in production mode"
    echo "  $0 --dev              # Start in development mode"
    echo "  $0 --stop             # Stop the server"
    echo "  PORT=8080 $0          # Start on port 8080"
}

# Main logic
case "${1:-}" in
    --dev|-d)
        install_deps
        start_dev
        ;;
    --prod|-p|"")
        install_deps
        start_prod
        ;;
    --stop|-s)
        stop_server
        ;;
    --status|-t)
        show_status
        ;;
    --help|-h)
        show_help
        ;;
    *)
        error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
