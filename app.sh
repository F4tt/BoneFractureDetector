#!/bin/bash
set -e

# Ensure writable Streamlit dir
mkdir -p /app/.streamlit
export STREAMLIT_HOME=/app/.streamlit

# Start FastAPI on port 7860
uvicorn api.main:app --host 0.0.0.0 --port 7860 &

# Start Streamlit on port 7861
streamlit run scripts/ui.py --server.port 7861 --server.address 0.0.0.0 &

# Keep container alive until both exit
wait
