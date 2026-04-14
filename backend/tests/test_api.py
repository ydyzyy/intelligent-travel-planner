"""API路由测试"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from app.models.schemas import TripPlan, DayPlan, Attraction, Location, Meal


class TestHealthCheck:
    """健康检查接口测试"""
    
    def test_health_check_success(self, client):
        """测试健康检查成功"""
        response = client.get("/api/trip/health")
        
        # 注意：实际测试中，由于Agent初始化可能失败，这里需要mock
        # 这个测试主要用于验证端点是否存在
        assert response.status_code in [200, 503]
    
    @patch('app.api.routes.trip.get_trip_planner_agent')
    def test_health_check_with_mock(self, mock_get_agent, client):
        """使用mock测试健康检查"""
        # 模拟Agent
        mock_agent = Mock()
        mock_agent.agent.name = "测试Agent"
        mock_agent.agent.list_tools.return_value = []
        mock_get_agent.return_value = mock_agent
        
        response = client.get("/api/trip/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'trip-planner'


class TestTripPlan:
    """旅行规划接口测试"""
    
    @patch('app.api.routes.trip.get_trip_planner_agent')
    def test_plan_trip_success(self, mock_get_agent, client, sample_trip_request):
        """测试成功生成旅行计划"""
        # 模拟Agent返回的旅行计划
        mock_plan = TripPlan(
            city="北京",
            start_date="2025-06-01",
            end_date="2025-06-03",
            days=[],
            overall_suggestions="测试建议"
        )
        
        mock_agent = Mock()
        mock_agent.plan_trip.return_value = mock_plan
        mock_get_agent.return_value = mock_agent
        
        response = client.post("/api/trip/plan", json=sample_trip_request.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['message'] == "旅行计划生成成功"
        assert 'data' in data
    
    def test_plan_trip_missing_fields(self, client):
        """测试缺少必填字段的请求"""
        invalid_request = {
            "city": "北京",
            # 缺少其他必填字段
        }
        
        response = client.post("/api/trip/plan", json=invalid_request)
        
        assert response.status_code == 422  # 验证错误
    
    def test_plan_trip_invalid_days(self, client):
        """测试无效的天数"""
        invalid_request = {
            "city": "北京",
            "start_date": "2025-06-01",
            "end_date": "2025-06-03",
            "travel_days": 0,  # 无效：小于1
            "transportation": "公共交通",
            "accommodation": "酒店"
        }
        
        response = client.post("/api/trip/plan", json=invalid_request)
        
        assert response.status_code == 422  # 验证错误
    
    @patch('app.api.routes.trip.get_trip_planner_agent')
    def test_plan_trip_with_all_fields(self, mock_get_agent, client):
        """测试包含所有字段的请求"""
        request_data = {
            "city": "上海",
            "start_date": "2025-07-01",
            "end_date": "2025-07-05",
            "travel_days": 5,
            "transportation": "自驾",
            "accommodation": "豪华酒店",
            "preferences": ["美食", "购物", "文化"],
            "free_text_input": "希望安排一些特色餐厅"
        }
        
        mock_plan = TripPlan(
            city="上海",
            start_date="2025-07-01",
            end_date="2025-07-05",
            days=[],
            overall_suggestions="测试建议"
        )
        
        mock_agent = Mock()
        mock_agent.plan_trip.return_value = mock_plan
        mock_get_agent.return_value = mock_agent
        
        response = client.post("/api/trip/plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    
    @patch('app.api.routes.trip.get_trip_planner_agent')
    def test_plan_trip_agent_error(self, mock_get_agent, client, sample_trip_request):
        """测试Agent出错的情况"""
        mock_agent = Mock()
        mock_agent.plan_trip.side_effect = Exception("Agent处理失败")
        mock_get_agent.return_value = mock_agent
        
        response = client.post("/api/trip/plan", json=sample_trip_request.dict())
        
        assert response.status_code == 500
        data = response.json()
        assert 'detail' in data


class TestAPIRoutes:
    """API路由综合测试"""
    
    def test_api_prefix(self, client):
        """测试API前缀"""
        # 测试不存在的路由
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_trip_router_exists(self, client):
        """测试旅行路由器存在"""
        # 健康检查端点应该存在
        response = client.get("/api/trip/health")
        assert response.status_code in [200, 503]  # 取决于Agent状态
    
    @patch('app.api.routes.trip.get_trip_planner_agent')
    def test_complete_trip_workflow(self, mock_get_agent, client, sample_trip_request):
        """测试完整的旅行规划工作流程"""
        # 创建详细的模拟旅行计划
        location = Location(longitude=116.397128, latitude=39.916527)
        attraction = Attraction(
            name="故宫",
            address="北京",
            location=location,
            visit_duration=180,
            description="著名景点",
            ticket_price=60
        )
        meal = Meal(type="lunch", name="烤鸭", estimated_cost=100)
        day_plan = DayPlan(
            date="2025-06-01",
            day_index=0,
            description="第一天",
            transportation="公共交通",
            accommodation="酒店",
            attractions=[attraction],
            meals=[meal]
        )
        
        mock_plan = TripPlan(
            city="北京",
            start_date="2025-06-01",
            end_date="2025-06-03",
            days=[day_plan],
            overall_suggestions="建议提前预订"
        )
        
        mock_agent = Mock()
        mock_agent.plan_trip.return_value = mock_plan
        mock_get_agent.return_value = mock_agent
        
        # 发送请求
        response = client.post("/api/trip/plan", json=sample_trip_request.dict())
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['city'] == "北京"
        assert len(data['data']['days']) == 1
        assert data['data']['days'][0]['attractions'][0]['name'] == "故宫"


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_json(self, client):
        """测试无效JSON"""
        response = client.post(
            "/api/trip/plan",
            content="invalid json",
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_wrong_content_type(self, client, sample_trip_request):
        """测试错误的内容类型"""
        response = client.post(
            "/api/trip/plan",
            data=sample_trip_request.dict(),
            headers={"content-type": "application/x-www-form-urlencoded"}
        )
        
        # FastAPI会尝试验证请求体
        assert response.status_code in [422, 400]
