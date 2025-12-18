@echo off
echo ========================================
echo Intel Iris Xe GPU Setup for TensorFlow
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing TensorFlow DirectML plugin...
echo This enables Intel GPU acceleration
echo.

pip install tensorflow-directml-plugin

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your Intel Iris Xe GPU is now ready for training
echo Run: python scripts\train_model_gpu.py
echo.
pause
