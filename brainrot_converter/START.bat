@echo off
REM Brainrot Converter - Complete Startup Script for Windows

echo.
echo ========================================
echo  Brainrot Textbook Converter - Startup
echo ========================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Ollama is not installed!
    echo Please download and install Ollama from: https://ollama.ai
    echo.
    pause
    exit /b 1
)

echo [1] Starting Ollama service...
echo Please wait (this may take a minute if Ollama isn't already running)
echo.

REM Start Ollama in a new window (it will run in background)
start "Ollama" ollama serve

REM Wait for Ollama to start
echo [2] Waiting for Ollama to initialize...
timeout /t 3 /nobreak

REM Check if Ollama is responsive
echo [3] Checking Ollama connection...
:check_ollama
curl -s http://localhost:11434/api/tags >nul 2>nul
if %errorlevel% neq 0 (
    echo Still waiting for Ollama...
    timeout /t 2 /nobreak
    goto check_ollama
)

echo [SUCCESS] Ollama is running!
echo.

REM Pull Mistral model if not already present
echo [4] Ensuring Mistral 7B model is available...
ollama pull mistral

echo.
echo [5] Starting Brainrot Converter Flask App...
cd /d "%~dp0"

REM Activate virtual environment and start Flask
call venv\Scripts\activate.bat
python app.py

pause
