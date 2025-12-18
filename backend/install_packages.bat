@echo off
echo Installing EcoVision Backend Dependencies...
echo.

call venv\Scripts\activate.bat

echo Step 1: Installing NumPy (pre-built wheel)...
pip install numpy

echo.
echo Step 2: Installing core ML packages...
pip install tensorflow opencv-python Pillow

echo.
echo Step 3: Installing web framework...
pip install fastapi uvicorn[standard] python-multipart

echo.
echo Step 4: Installing data processing packages...
pip install scikit-learn pandas

echo.
echo Step 5: Installing utilities...
pip install python-dotenv pydantic pydantic-settings tqdm

echo.
echo Step 6: Installing visualization packages...
pip install matplotlib seaborn

echo.
echo Step 7: Installing albumentations...
pip install albumentations

echo.
echo ===================================
echo Installation Complete!
echo ===================================
pause
