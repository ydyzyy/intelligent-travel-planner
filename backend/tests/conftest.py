"""测试配置文件和fixtures"""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# 导入应用
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.api.main import app
from app.models.schemas import TripRequest, Location, Attraction, Meal, DayPlan, TripPlan


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_trip_request() -> TripRequest:
    """创建示例旅行请求"""
    return TripRequest(
        city="北京",
        start_date="2025-06-01",
        end_date="2025-06-03",
        travel_days=3,
        transportation="公共交通",
        accommodation="经济型酒店",
        preferences=["历史文化", "美食"],
        free_text_input="希望多安排一些博物馆"
    )


@pytest.fixture
def sample_location() -> Location:
    """创建示例位置"""
    return Location(longitude=116.397128, latitude=39.916527)


@pytest.fixture
def sample_attraction(sample_location: Location) -> Attraction:
    """创建示例景点"""
    return Attraction(
        name="故宫博物院",
        address="北京市东城区景山前街4号",
        location=sample_location,
        visit_duration=180,
        description="中国明清两代的皇家宫殿",
        category="历史文化",
        rating=4.8,
        ticket_price=60
    )


@pytest.fixture
def sample_meal() -> Meal:
    """创建示例餐饮"""
    return Meal(
        type="lunch",
        name="北京烤鸭",
        address="王府井大街",
        description="正宗北京烤鸭",
        estimated_cost=150
    )


@pytest.fixture
def sample_day_plan(
    sample_attraction: Attraction,
    sample_meal: Meal
) -> DayPlan:
    """创建示例日计划"""
    return DayPlan(
        date="2025-06-01",
        day_index=0,
        description="第一天：探索北京历史文化",
        transportation="公共交通",
        accommodation="经济型酒店",
        attractions=[sample_attraction],
        meals=[sample_meal]
    )


@pytest.fixture
def sample_trip_plan(sample_day_plan: DayPlan) -> TripPlan:
    """创建示例旅行计划"""
    return TripPlan(
        city="北京",
        start_date="2025-06-01",
        end_date="2025-06-03",
        days=[sample_day_plan],
        overall_suggestions="建议提前预订门票，注意天气变化"
    )


@pytest.fixture
def mock_env_vars(monkeypatch):
    """模拟环境变量"""
    monkeypatch.setenv("AMAP_API_KEY", "test_amap_key")
    monkeypatch.setenv("LLM_API_KEY", "test_llm_key")
    monkeypatch.setenv("LLM_MODEL", "gpt-3.5-turbo")
