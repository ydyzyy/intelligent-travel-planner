"""Agent相关测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agents.trip_planner_agent import (
    MultiAgentTripPlanner,
    get_trip_planner_agent,
    ATTRACTION_AGENT_PROMPT,
    WEATHER_AGENT_PROMPT,
    PLANNER_AGENT_PROMPT
)
from app.models.schemas import TripRequest


class TestPrompts:
    """提示词测试"""
    
    def test_attraction_agent_prompt_exists(self):
        """测试景点Agent提示词存在"""
        assert ATTRACTION_AGENT_PROMPT is not None
        assert len(ATTRACTION_AGENT_PROMPT) > 0
        assert "工具调用格式" in ATTRACTION_AGENT_PROMPT
    
    def test_weather_agent_prompt_exists(self):
        """测试天气Agent提示词存在"""
        assert WEATHER_AGENT_PROMPT is not None
        assert len(WEATHER_AGENT_PROMPT) > 0
        assert "maps_weather" in WEATHER_AGENT_PROMPT
    
    def test_planner_agent_prompt_exists(self):
        """测试规划Agent提示词存在"""
        assert PLANNER_AGENT_PROMPT is not None
        assert len(PLANNER_AGENT_PROMPT) > 0
        assert "JSON" in PLANNER_AGENT_PROMPT


class TestMultiAgentTripPlanner:
    """多智能体旅行规划器测试"""
    
    @patch('app.agents.trip_planner_agent.get_llm')
    @patch('hello_agents.tools.MCPTool')
    @patch('hello_agents.SimpleAgent')
    def test_init_success(self, mock_simple_agent, mock_mcp_tool, mock_get_llm, mock_env_vars):
        """测试初始化成功"""
        # 模拟LLM
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        # 模拟MCP工具
        mock_tool = Mock()
        mock_tool._available_tools = []
        mock_mcp_tool.return_value = mock_tool
        
        # 模拟SimpleAgent
        mock_agent = Mock()
        mock_agent.list_tools.return_value = []
        mock_simple_agent.return_value = mock_agent
        
        # 创建规划器
        planner = MultiAgentTripPlanner()
        
        assert planner.llm == mock_llm
        assert hasattr(planner, 'attraction_agent')
        assert hasattr(planner, 'weather_agent')
        assert hasattr(planner, 'hotel_agent')
        assert hasattr(planner, 'planner_agent')
    
    @patch('app.agents.trip_planner_agent.get_llm')
    def test_init_failure(self, mock_get_llm, mock_env_vars):
        """测试初始化失败"""
        mock_get_llm.side_effect = Exception("LLM初始化失败")
        
        with pytest.raises(Exception):
            MultiAgentTripPlanner()
    
    @patch('app.agents.trip_planner_agent.get_llm')
    @patch('hello_agents.tools.MCPTool')
    @patch('hello_agents.SimpleAgent')
    def test_build_attraction_query(self, mock_simple_agent, mock_mcp_tool, mock_get_llm, mock_env_vars):
        """测试构建景点搜索查询"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_tool = Mock()
        mock_tool._available_tools = []
        mock_mcp_tool.return_value = mock_tool
        
        mock_agent = Mock()
        mock_agent.list_tools.return_value = []
        mock_simple_agent.return_value = mock_agent
        
        planner = MultiAgentTripPlanner()
        
        request = TripRequest(
            city="北京",
            start_date="2025-06-01",
            end_date="2025-06-03",
            travel_days=3,
            transportation="公共交通",
            accommodation="酒店",
            preferences=["历史文化"]
        )
        
        query = planner._build_attraction_query(request)
        
        assert "北京" in query
        assert "历史文化" in query
        assert "TOOL_CALL" in query
    
    @patch('app.agents.trip_planner_agent.get_llm')
    @patch('hello_agents.tools.MCPTool')
    @patch('hello_agents.SimpleAgent')
    def test_build_planner_query(self, mock_simple_agent, mock_mcp_tool, mock_get_llm, mock_env_vars):
        """测试构建规划器查询"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_tool = Mock()
        mock_tool._available_tools = []
        mock_mcp_tool.return_value = mock_tool
        
        mock_agent = Mock()
        mock_agent.list_tools.return_value = []
        mock_simple_agent.return_value = mock_agent
        
        planner = MultiAgentTripPlanner()
        
        request = TripRequest(
            city="上海",
            start_date="2025-07-01",
            end_date="2025-07-03",
            travel_days=3,
            transportation="自驾",
            accommodation="豪华酒店",
            preferences=["美食"],
            free_text_input="希望安排特色餐厅"
        )
        
        query = planner._build_planner_query(
            request,
            attractions="景点信息",
            weather="天气信息",
            hotels="酒店信息"
        )
        
        assert "上海" in query
        assert "景点信息" in query
        assert "天气信息" in query
        assert "酒店信息" in query
        assert "特色餐厅" in query
    
    @patch('app.agents.trip_planner_agent.get_llm')
    @patch('hello_agents.tools.MCPTool')
    @patch('hello_agents.SimpleAgent')
    def test_parse_response_with_json_block(self, mock_simple_agent, mock_mcp_tool, mock_get_llm, mock_env_vars):
        """测试解析包含JSON代码块的响应"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_tool = Mock()
        mock_tool._available_tools = []
        mock_mcp_tool.return_value = mock_tool
        
        mock_agent = Mock()
        mock_agent.list_tools.return_value = []
        mock_simple_agent.return_value = mock_agent
        
        planner = MultiAgentTripPlanner()
        
        response = '''
        这是旅行计划：
        ```json
        {
            "city": "北京",
            "start_date": "2025-06-01",
            "end_date": "2025-06-03",
            "days": [],
            "overall_suggestions": "测试建议"
        }
        ```
        '''
        
        request = TripRequest(
            city="北京",
            start_date="2025-06-01",
            end_date="2025-06-03",
            travel_days=3,
            transportation="公共交通",
            accommodation="酒店"
        )
        
        plan = planner._parse_response(response, request)
        
        assert plan.city == "北京"
        assert plan.start_date == "2025-06-01"
    
    @patch('app.agents.trip_planner_agent.get_llm')
    @patch('hello_agents.tools.MCPTool')
    @patch('hello_agents.SimpleAgent')
    def test_parse_response_fallback(self, mock_simple_agent, mock_mcp_tool, mock_get_llm, mock_env_vars):
        """测试解析失败时使用备用方案"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_tool = Mock()
        mock_tool._available_tools = []
        mock_mcp_tool.return_value = mock_tool
        
        mock_agent = Mock()
        mock_agent.list_tools.return_value = []
        mock_simple_agent.return_value = mock_agent
        
        planner = MultiAgentTripPlanner()
        
        # 无效的响应
        response = "这不是有效的JSON响应"
        
        request = TripRequest(
            city="北京",
            start_date="2025-06-01",
            end_date="2025-06-03",
            travel_days=3,
            transportation="公共交通",
            accommodation="酒店"
        )
        
        plan = planner._parse_response(response, request)
        
        # 应该返回备用计划
        assert plan.city == "北京"
        assert len(plan.days) == 3
    
    @patch('app.agents.trip_planner_agent.get_llm')
    @patch('hello_agents.tools.MCPTool')
    @patch('hello_agents.SimpleAgent')
    def test_create_fallback_plan(self, mock_simple_agent, mock_mcp_tool, mock_get_llm, mock_env_vars):
        """测试创建备用计划"""
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_tool = Mock()
        mock_tool._available_tools = []
        mock_mcp_tool.return_value = mock_tool
        
        mock_agent = Mock()
        mock_agent.list_tools.return_value = []
        mock_simple_agent.return_value = mock_agent
        
        planner = MultiAgentTripPlanner()
        
        request = TripRequest(
            city="广州",
            start_date="2025-08-01",
            end_date="2025-08-02",
            travel_days=2,
            transportation="地铁",
            accommodation="经济型"
        )
        
        plan = planner._create_fallback_plan(request)
        
        assert plan.city == "广州"
        assert len(plan.days) == 2
        assert plan.days[0].day_index == 0
        assert plan.days[1].day_index == 1
    
    @patch('app.agents.trip_planner_agent.get_llm')
    @patch('hello_agents.tools.MCPTool')
    @patch('hello_agents.SimpleAgent')
    def test_plan_trip_workflow(self, mock_simple_agent, mock_mcp_tool, mock_get_llm, mock_env_vars):
        """测试完整的旅行规划工作流程"""
        # 重置全局变量
        import app.agents.trip_planner_agent as agent_module
        agent_module._multi_agent_planner = None
        
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_tool = Mock()
        mock_tool._available_tools = []
        mock_mcp_tool.return_value = mock_tool
        
        # 为不同的Agent设置不同的返回值
        attraction_agent = Mock()
        attraction_agent.run.return_value = "景点搜索结果"
        attraction_agent.list_tools.return_value = []
        
        weather_agent = Mock()
        weather_agent.run.return_value = "天气查询结果"
        weather_agent.list_tools.return_value = []
        
        hotel_agent = Mock()
        hotel_agent.run.return_value = "酒店搜索结果"
        hotel_agent.list_tools.return_value = []
        
        planner_agent = Mock()
        planner_agent.run.return_value = '''
        ```json
        {
            "city": "北京",
            "start_date": "2025-06-01",
            "end_date": "2025-06-03",
            "days": [],
            "overall_suggestions": "测试建议"
        }
        ```
        '''
        planner_agent.list_tools.return_value = []
        
        # 按顺序返回不同的Agent实例
        mock_simple_agent.side_effect = [
            attraction_agent,
            weather_agent,
            hotel_agent,
            planner_agent
        ]
        
        # 创建规划器
        planner = MultiAgentTripPlanner()
        
        # Mock plan_trip方法内部的agent.run调用
        planner.attraction_agent = attraction_agent
        planner.weather_agent = weather_agent
        planner.hotel_agent = hotel_agent
        planner.planner_agent = planner_agent
        
        request = TripRequest(
            city="北京",
            start_date="2025-06-01",
            end_date="2025-06-03",
            travel_days=3,
            transportation="公共交通",
            accommodation="酒店",
            preferences=["文化"]
        )
        
        plan = planner.plan_trip(request)
        
        assert plan.city == "北京"
        attraction_agent.run.assert_called_once()
        weather_agent.run.assert_called_once()
        hotel_agent.run.assert_called_once()
        planner_agent.run.assert_called_once()


class TestGetTripPlannerAgent:
    """获取旅行规划器单例测试"""
    
    @patch('app.agents.trip_planner_agent.get_llm')
    @patch('hello_agents.tools.MCPTool')
    @patch('hello_agents.SimpleAgent')
    def test_singleton_pattern(self, mock_simple_agent, mock_mcp_tool, mock_get_llm, mock_env_vars):
        """测试单例模式"""
        # 重置全局变量
        import app.agents.trip_planner_agent as agent_module
        agent_module._multi_agent_planner = None
        
        mock_llm = Mock()
        mock_get_llm.return_value = mock_llm
        
        mock_tool = Mock()
        mock_tool._available_tools = []
        mock_mcp_tool.return_value = mock_tool
        
        mock_agent = Mock()
        mock_agent.list_tools.return_value = []
        mock_simple_agent.return_value = mock_agent
        
        # 第一次调用
        planner1 = get_trip_planner_agent()
        
        # 第二次调用
        planner2 = get_trip_planner_agent()
        
        # 应该是同一个实例
        assert planner1 is planner2
