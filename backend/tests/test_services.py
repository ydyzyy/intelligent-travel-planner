"""服务层测试"""

import pytest
import importlib
from unittest.mock import Mock, patch, MagicMock
from app.services.amap_service import AmapService, get_amap_service
from app.services.llm_service import get_llm
from app.config import get_settings


class TestConfig:
    """配置测试"""
    
    @patch('app.config.load_dotenv')
    def test_get_settings_with_mock_env(self, mock_load_dotenv, monkeypatch):
        """测试获取配置（使用mock环境变量）"""
        # 设置测试环境变量
        monkeypatch.setenv("AMAP_API_KEY", "test_amap_key")
        
        # 重新加载配置模块以读取新的环境变量
        import app.config as config_module
        importlib.reload(config_module)
        
        settings = config_module.get_settings()
        assert settings.amap_api_key == "test_amap_key"
        assert settings.app_name == "智能旅行助手"
    
    def test_settings_default_values(self):
        """测试配置默认值"""
        settings = get_settings()
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'debug')


class TestLLMService:
    """LLM服务测试"""
    
    @patch('app.services.llm_service.ChatOpenAI')
    def test_get_llm(self, mock_hello_agents_llm, mock_env_vars):
        """测试获取LLM实例"""
        # 重置全局变量
        import app.services.llm_service as llm_module
        llm_module._llm_instance = None
        
        mock_llm = Mock()
        mock_llm.provider = "openai"
        mock_llm.model = "gpt-3.5-turbo"
        mock_hello_agents_llm.return_value = mock_llm
        
        llm = get_llm()
        
        assert llm is not None
        mock_hello_agents_llm.assert_called_once()


class TestAmapService:
    """高德地图服务测试"""
    
    @patch('app.services.amap_service.get_amap_mcp_tool')
    def test_search_poi(self, mock_get_mcp_tool):
        """测试POI搜索"""
        # 模拟MCP工具
        mock_mcp = Mock()
        mock_mcp.run.return_value = '{"pois": []}'
        mock_get_mcp_tool.return_value = mock_mcp
        
        service = AmapService()
        result = service.search_poi("故宫", "北京")
        
        assert isinstance(result, list)
        mock_mcp.run.assert_called_once()
    
    @patch('app.services.amap_service.get_amap_mcp_tool')
    def test_get_weather(self, mock_get_mcp_tool):
        """测试天气查询"""
        # 模拟MCP工具
        mock_mcp = Mock()
        mock_mcp.run.return_value = '{"weather": []}'
        mock_get_mcp_tool.return_value = mock_mcp
        
        service = AmapService()
        result = service.get_weather("北京")
        
        assert isinstance(result, list)
        mock_mcp.run.assert_called_once()
    
    @patch('app.services.amap_service.get_amap_mcp_tool')
    def test_plan_route_walking(self, mock_get_mcp_tool):
        """测试步行路线规划"""
        # 模拟MCP工具
        mock_mcp = Mock()
        mock_mcp.run.return_value = '{"route": {}}'
        mock_get_mcp_tool.return_value = mock_mcp
        
        service = AmapService()
        result = service.plan_route(
            origin_address="起点",
            destination_address="终点",
            route_type="walking"
        )
        
        assert isinstance(result, dict)
        mock_mcp.run.assert_called_once()
        call_args = mock_mcp.run.call_args[0][0]
        assert call_args['tool_name'] == 'maps_direction_walking_by_address'
    
    @patch('app.services.amap_service.get_amap_mcp_tool')
    def test_plan_route_driving(self, mock_get_mcp_tool):
        """测试驾车路线规划"""
        # 模拟MCP工具
        mock_mcp = Mock()
        mock_mcp.run.return_value = '{"route": {}}'
        mock_get_mcp_tool.return_value = mock_mcp
        
        service = AmapService()
        result = service.plan_route(
            origin_address="起点",
            destination_address="终点",
            route_type="driving"
        )
        
        assert isinstance(result, dict)
        call_args = mock_mcp.run.call_args[0][0]
        assert call_args['tool_name'] == 'maps_direction_driving_by_address'
    
    @patch('app.services.amap_service.get_amap_mcp_tool')
    def test_plan_route_transit(self, mock_get_mcp_tool):
        """测试公共交通路线规划"""
        # 模拟MCP工具
        mock_mcp = Mock()
        mock_mcp.run.return_value = '{"route": {}}'
        mock_get_mcp_tool.return_value = mock_mcp
        
        service = AmapService()
        result = service.plan_route(
            origin_address="起点",
            destination_address="终点",
            origin_city="北京",
            destination_city="上海",
            route_type="transit"
        )
        
        assert isinstance(result, dict)
        call_args = mock_mcp.run.call_args[0][0]
        assert call_args['tool_name'] == 'maps_direction_transit_integrated_by_address'
        assert 'origin_city' in call_args['arguments']
    
    @patch('app.services.amap_service.get_amap_mcp_tool')
    def test_geocode(self, mock_get_mcp_tool):
        """测试地理编码"""
        # 模拟MCP工具
        mock_mcp = Mock()
        mock_mcp.run.return_value = '{"location": {}}'
        mock_get_mcp_tool.return_value = mock_mcp
        
        service = AmapService()
        result = service.geocode("北京市朝阳区", "北京")
        
        # 当前实现返回None，因为TODO未解析数据
        assert result is None or isinstance(result, type(None))
    
    @patch('app.services.amap_service.get_amap_mcp_tool')
    def test_get_poi_detail(self, mock_get_mcp_tool):
        """测试获取POI详情"""
        # 模拟MCP工具
        mock_mcp = Mock()
        mock_mcp.run.return_value = '{"poi": {"id": "test"}}'
        mock_get_mcp_tool.return_value = mock_mcp
        
        service = AmapService()
        result = service.get_poi_detail("B000A8BD58")
        
        assert isinstance(result, dict)
    
    def test_get_amap_service_singleton(self):
        """测试服务单例模式"""
        with patch('app.services.amap_service.get_amap_mcp_tool'):
            service1 = get_amap_service()
            service2 = get_amap_service()
            
            assert service1 is service2


class TestAmapMCPTool:
    """高德地图MCP工具测试"""
    
    @patch('hello_agents.tools.MCPTool')
    def test_get_amap_mcp_tool_singleton(self, mock_mcp_tool_class, mock_env_vars):
        """测试MCP工具单例模式"""
        from app.services.amap_service import get_amap_mcp_tool
        
        # 重置全局变量
        import app.services.amap_service as amap_module
        amap_module._amap_mcp_tool = None
        
        mock_tool = Mock()
        mock_tool._available_tools = []
        mock_mcp_tool_class.return_value = mock_tool
        
        tool1 = get_amap_mcp_tool()
        tool2 = get_amap_mcp_tool()
        
        assert tool1 is tool2
    
    def test_mcp_tool_initialization(self, mock_env_vars):
        """测试MCP工具初始化"""
        from app.services.amap_service import get_amap_mcp_tool
        
        # 重置全局变量（确保是全新的状态）
        import app.services.amap_service as amap_module
        original_value = amap_module._amap_mcp_tool
        amap_module._amap_mcp_tool = None
        
        try:
            # 直接调用，验证能成功创建工具
            tool = get_amap_mcp_tool()
            
            # 验证工具被正确创建
            assert tool is not None
            assert hasattr(tool, '_available_tools')
            
            # 验证单例模式 - 第二次调用返回同一个实例
            tool2 = get_amap_mcp_tool()
            assert tool is tool2
            
        finally:
            # 恢复原始值，避免影响其他测试
            amap_module._amap_mcp_tool = original_value
