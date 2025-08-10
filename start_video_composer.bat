@echo off
echo ================================================
echo    🎬  Himawari8 视频合成器启动中...
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：Python未安装或未添加到PATH
    echo    请安装Python并确保python命令可用
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import cv2, PIL, numpy, tqdm" >nul 2>&1
if errorlevel 1 (
    echo 📦 正在安装依赖库...
    pip install opencv-python pillow numpy tqdm
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请手动安装
        pause
        exit /b 1
    )
)

REM 启动视频合成器
echo 🚀 启动视频合成器...
python video_composer.py

echo.
echo ✅ 视频合成器已关闭
pause