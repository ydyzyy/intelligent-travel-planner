@echo off
chcp 65001 >nul
title 智能旅行规划助手 - 一键启动

echo.
echo ======================================================================
echo 🌍 智能旅行规划助手 - 一键启动
echo ======================================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.
echo 🚀 正在启动系统...
echo.

REM 运行启动脚本
python start.py

pause
