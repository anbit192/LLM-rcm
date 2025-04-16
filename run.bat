call "%~dp0venv\Scripts\activate.bat"

start "Backend" cmd /k "cd /d "%~dp0src" && echo Starting backend... && uvicorn main:app --reload"
start "Frontend" cmd /k "cd /d "%~dp0src" && echo Starting frontend-2... && streamlit run frontend-2.py"
