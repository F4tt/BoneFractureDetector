#!/bin/bash
set -e

# 1. Set các thư mục writable
export STREAMLIT_HOME=/app/.streamlit
export MPLCONFIGDIR=/app/.config/matplotlib
export YOLO_CONFIG_DIR=/app/.config/ultralytics

mkdir -p $STREAMLIT_HOME $MPLCONFIGDIR $YOLO_CONFIG_DIR

# 2. Chạy Streamlit trên 7860 (Hugging Face Space chỉ expose cổng này)
exec streamlit run scripts/ui.py --server.port 7860 --server.address 0.0.0.0
