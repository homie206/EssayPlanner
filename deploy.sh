#!/usr/bin/env bash
set -e

BACKEND_SESSION="ai4ed-backend"
FRONTEND_SESSION="ai4ed-frontend"
BACKEND_PORT=8000
FRONTEND_PORT=8501

echo "Pulling latest from main..."
git pull origin main

echo "Installing/updating dependencies..."
uv sync --frozen --no-dev

echo "Stopping existing services..."
screen -S "$BACKEND_SESSION" -X quit 2>/dev/null || true
screen -S "$FRONTEND_SESSION" -X quit 2>/dev/null || true
sleep 2

echo "Starting backend..."
screen -dmS "$BACKEND_SESSION" uv run uvicorn bin.MultiAgentSystem.app:app \
    --host 0.0.0.0 --port "$BACKEND_PORT" --workers 2

echo "Waiting for backend to be ready..."
for i in $(seq 1 30); do
    if python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:$BACKEND_PORT/docs')" 2>/dev/null; then
        echo "  Backend is ready."
        break
    fi
    echo "  waiting... ($i/30)"
    sleep 2
done

echo "Starting frontend..."
screen -dmS "$FRONTEND_SESSION" bash -c \
    "BACKEND_URL=http://localhost:$BACKEND_PORT uv run streamlit run \
    bin/MultiAgentSystem/front_end.py \
    --server.port $FRONTEND_PORT --server.address 0.0.0.0"

echo ""
echo "Done. Services running:"
echo "  Backend:  http://$(hostname -I | awk '{print $1}'):$BACKEND_PORT/docs"
echo "  Frontend: http://$(hostname -I | awk '{print $1}'):$FRONTEND_PORT"
echo ""
echo "To view logs:"
echo "  screen -r $BACKEND_SESSION"
echo "  screen -r $FRONTEND_SESSION"
echo "  (Ctrl+A then D to detach from screen)"
