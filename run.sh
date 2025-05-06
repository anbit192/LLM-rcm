#!/bin/bash

# Kích hoạt virtual environment
source "$(dirname "$0")/venv/bin/activate"

# Mở backend trong cửa sổ konsole riêng biệt
konsole --separate -e bash -c "cd \"$(dirname "$0")/src\" && echo 'Starting backend...' && uvicorn main:app --reload; exec bash" &

# Mở frontend trong cửa sổ konsole riêng biệt
konsole --separate -e bash -c "cd \"$(dirname "$0")/src\" && echo 'Starting frontend-2...' && streamlit run frontend-2.py; exec bash" &
