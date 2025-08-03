#!/bin/bash
set -e

# Ensure writable Streamlit dir
mkdir -p /app/.streamlit
export STREAMLIT_HOME=/app/.streamlit

# Start FastAPI (internal)
uvicorn api.main:app --host 0.0.0.0 --port 7861 &

# Start Streamlit (public)
streamlit run scripts/ui.py --server.port 7860 --server.address 0.0.0.0
