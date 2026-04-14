"""快速验证测试 - 确认测试环境配置正确"""

import pytest


def test_python_version():
    """测试Python版本"""
    import sys
    assert sys.version_info >= (3, 10), "需要Python 3.10或更高版本"
    print(f"✅ Python版本: {sys.version}")


def test_imports():
    """测试关键模块可以导入"""
    # 测试FastAPI
    from fastapi import FastAPI
    assert FastAPI is not None
    
    # 测试Pydantic
    from pydantic import BaseModel
    assert BaseModel is not None
    
    # 测试pytest
    import pytest
    assert pytest is not None
    
    print("✅ 所有关键模块导入成功")


def test_app_import():
    """测试应用可以导入"""
    from app.api.main import app
    assert app is not None
    # 修复：使用实际的应用标题
    assert app.title == "智能旅行助手"
    
    print(f"✅ 应用导入成功: {app.title}")


def test_app_title():
    """测试应用标题"""
    from app.api.main import app
    assert app.title == "智能旅行助手"


def test_models_import():
    """测试数据模型可以导入"""
    from app.models.schemas import (
        TripRequest,
        TripPlan,
        Location,
        Attraction,
        Meal,
        DayPlan
    )
    
    assert TripRequest is not None
    assert TripPlan is not None
    
    print("✅ 数据模型导入成功")


def test_config_import():
    """测试配置可以导入"""
    from app.config import get_settings
    
    settings = get_settings()
    assert settings is not None
    
    print("✅ 配置导入成功")


if __name__ == "__main__":
    # 直接运行此文件进行快速验证
    print("="*60)
    print("🧪 快速验证测试环境")
    print("="*60)
    
    test_python_version()
    test_imports()
    test_app_import()
    test_models_import()
    test_config_import()
    
    print("\n✅ 所有验证测试通过！测试环境配置正确。")
