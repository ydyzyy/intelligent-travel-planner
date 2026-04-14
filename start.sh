#!/bin/bash

# 智能旅行规划助手 - 一键启动脚本 (Linux/Mac)

echo ""
echo "======================================================================"
echo "🌍 智能旅行规划助手 - 一键启动"
echo "======================================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到Python3，请先安装Python 3.10+"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 未检测到Node.js，请先安装Node.js 16+"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""
echo "🚀 正在启动系统..."
echo ""

# 运行启动脚本
python3 start.py
