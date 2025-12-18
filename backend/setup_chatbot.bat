@echo off
echo ========================================
echo EcoBot Chatbot Setup
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing Google Gemini SDK...
echo.

pip install google-generativeai

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Get API key from: https://aistudio.google.com/app/apikey
echo 2. Create .env file: copy .env.example .env
echo 3. Add your API key to .env file: GEMINI_API_KEY=your_key_here
echo 4. Restart backend: python app/main.py
echo.
pause
