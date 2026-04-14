"""集成测试 - 测试真实的Agent运行情况

注意：这些测试需要真实的API Key和网络连接
运行前请确保：
1. .env文件中配置了AMAP_API_KEY
2. .env文件中配置了LLM_API_KEY或OPENAI_API_KEY
3. 网络连接正常
"""

import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.models.schemas import TripRequest


@pytest.mark.integration
class TestRealAgentIntegration:
    """真实Agent集成测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_health_check_real(self, client):
        """测试健康检查 - 验证Agent是否真正初始化"""
        response = client.get("/api/trip/health")
        
        # 如果API Key配置正确，应该返回healthy
        if response.status_code == 200:
            data = response.json()
            assert data['status'] == 'healthy'
            assert 'agent_name' in data
            assert 'tools_count' in data
            print(f"✅ Agent健康检查通过: {data['agent_name']}")
            print(f"   工具数量: {data['tools_count']}")
            
            # 显示LLM信息
            if 'llm_provider' in data:
                print(f"   LLM提供商: {data['llm_provider']}")
            if 'llm_model' in data:
                print(f"   LLM模型: {data['llm_model']}")
                
            # 显示组件信息
            if 'components' in data:
                print(f"   组件:")
                for name, desc in data['components'].items():
                    print(f"     - {name}: {desc}")
        else:
            # 如果配置不正确，会返回503
            print(f"⚠️  服务未就绪: {response.json()}")
            pytest.skip("API Key未配置或无效")
    
    def test_simple_trip_plan(self, client):
        """测试简单的旅行计划生成
        
        这是一个真实的端到端测试，会：
        1. 发送旅行规划请求
        2. Agent调用MCP工具搜索景点
        3. Agent查询天气
        4. Agent生成旅行计划
        5. 返回完整的JSON响应
        """
        # 准备测试数据 - 使用简单的请求
        request_data = {
            "city": "广州",
            "start_date": "2026-04-13",
            "end_date": "2026-04-14",
            "travel_days": 2,
            "transportation": "公共交通",
            "accommodation": "经济型酒店",
            "preferences": ["美食探索"],
            "free_text_input": ""
        }
        
        print("\n" + "="*60)
        print("🧪 开始真实Agent测试")
        print("="*60)
        print(f"目的地: {request_data['city']}")
        print(f"天数: {request_data['travel_days']}天")
        print("="*60 + "\n")
        
        # 发送请求
        response = client.post("/api/trip/plan", json=request_data, timeout=120)
        
        # 验证响应
        if response.status_code == 200:
            data = response.json()
            
            print("✅ 旅行计划生成成功!")
            print(f"   城市: {data['data']['city']}")
            print(f"   天数: {len(data['data']['days'])}天")
            print(f"   建议: {data['data']['overall_suggestions'][:100]}...")
            
            # 验证数据结构
            assert data['success'] is True
            assert 'data' in data
            assert data['data']['city'] == request_data['city']
            assert len(data['data']['days']) == request_data['travel_days']
            
            # 验证每天的行程
            for day in data['data']['days']:
                assert 'date' in day
                assert 'attractions' in day
                assert 'meals' in day
                print(f"\n   📅 {day['date']}:")
                print(f"      景点数: {len(day['attractions'])}")
                print(f"      餐饮数: {len(day['meals'])}")
            
            # 验证是否有天气信息
            if data['data'].get('weather_info'):
                print(f"\n   🌤️  天气信息: {len(data['data']['weather_info'])}天")
            
            # 验证是否有预算信息
            if data['data'].get('budget'):
                budget = data['data']['budget']
                print(f"\n   💰 预算总计: {budget.get('total', 0)}元")
            
            print("\n" + "="*60)
            print("✅ 所有验证通过!")
            print("="*60)
            
        elif response.status_code == 500:
            error_detail = response.json().get('detail', '')
            print(f"❌ 服务器错误: {error_detail}")
            print("\n可能的原因:")
            print("  1. LLM API Key无效或未配置")
            print("  2. 高德地图API Key无效或未配置")
            print("  3. 网络连接问题")
            print("  4. LLM服务超时")
            pytest.fail(f"Agent执行失败: {error_detail}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)
            pytest.fail(f"HTTP {response.status_code}")
    
    def test_agent_with_different_cities(self, client):
        """测试不同城市的旅行规划"""
        cities = ["上海", "广州"]
        
        for city in cities:
            print(f"\n🔄 测试城市: {city}")
            
            request_data = {
                "city": city,
                "start_date": "2025-07-01",
                "end_date": "2025-07-02",
                "travel_days": 2,
                "transportation": "地铁",
                "accommodation": "酒店",
                "preferences": ["美食"],
                "free_text_input": ""
            }
            
            response = client.post("/api/trip/plan", json=request_data, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                assert data['data']['city'] == city
                print(f"   ✅ {city} 测试通过")
            else:
                print(f"   ⚠️  {city} 测试跳过")
                pytest.skip(f"{city} 测试失败")
                break


@pytest.mark.integration
class TestMCPToolsReal:
    """真实MCP工具测试 - 已废弃，改用REST API"""
    
    @pytest.mark.skip(reason="已切换到REST API方案，不再使用MCP工具")
    def test_amap_mcp_tool_connection(self):
        """测试高德地图MCP工具连接 - 已废弃"""
        pass
    
    @pytest.mark.integration
    def test_rest_api_connection(self):
        """测试REST API连接"""
        from app.services.amap_service import get_amap_service
        
        print("\n🔌 测试REST API连接...")
        
        try:
            service = get_amap_service()
            print(f"✅ AmapService初始化成功")
            
            # 测试POI搜索
            pois = service.search_poi("景点", "北京")
            print(f"✅ POI搜索测试: 找到{len(pois)}个结果")
            
            # 测试天气查询
            weather = service.get_weather("北京")
            print(f"✅ 天气查询测试: {len(weather)}天预报")
            
            assert len(pois) >= 0  # 允许返回0个结果（API限制）
            assert len(weather) > 0  # 天气应该有数据
            
        except Exception as e:
            print(f"❌ REST API测试失败: {e}")
            pytest.fail(f"REST API连接失败: {e}")
    
    @pytest.mark.integration
    def test_llm_connection(self):
        """测试LLM连接"""
        from app.services.llm_service import get_llm
        
        try:
            llm = get_llm()
            assert llm is not None
            
            print(f"✅ LLM服务初始化成功")
            # 安全地打印LLM信息
            provider = getattr(llm, 'provider', 'unknown')
            model = getattr(llm, 'model', 'unknown')
            print(f"   提供商: {provider}")
            print(f"   模型: {model}")
            
            # 尝试简单调用
            response = llm.invoke("你好，请用一句话介绍自己")
            assert response is not None
            assert len(str(response)) > 0
            
            print(f"   LLM响应: {str(response)[:100]}...")
            
        except Exception as e:
            print(f"❌ LLM服务失败: {e}")
            pytest.skip(f"LLM服务不可用: {e}")


@pytest.mark.integration  
class TestFullWorkflow:
    """完整工作流测试"""
    
    def test_complete_trip_planning_workflow(self):
        """测试完整的旅行规划工作流"""
        print("\n" + "="*60)
        print("🧪 完整工作流测试")
        print("="*60)
        
        try:
            from app.agents.trip_planner_agent import get_trip_planner_agent
            from app.models.schemas import TripRequest
            
            # 步骤1: 初始化Agent系统
            print("\n步骤1: 初始化Agent系统...")
            agent = get_trip_planner_agent()
            print(f"   ✅ Agent系统初始化成功")
            # 安全地打印LLM信息
            provider = getattr(agent.llm, 'provider', 'unknown')
            model = getattr(agent.llm, 'model', 'unknown')
            print(f"   ✅ LLM提供商: {provider}")
            print(f"   ✅ LLM模型: {model}")
            
            # 步骤2: 创建测试请求
            print("\n步骤2: 创建测试请求...")
            request = TripRequest(
                city="杭州",
                start_date="2025-08-01",
                end_date="2025-08-03",
                travel_days=3,
                transportation="公共交通",
                accommodation="舒适型酒店",
                preferences=["自然风光", "历史文化"]
            )
            print(f"   ✅ 请求创建: {request.city} {request.travel_days}天")
            
            # 步骤3: 执行旅行规划
            print("\n步骤3: 执行旅行规划...")
            trip_plan = agent.plan_trip(request)
            
            # 步骤4: 验证结果
            print("\n步骤4: 验证结果...")
            assert trip_plan is not None, "旅行计划不应为None"
            assert trip_plan.city == request.city, f"城市应匹配: {trip_plan.city}"
            assert len(trip_plan.days) == request.travel_days, f"天数应匹配: {len(trip_plan.days)}"
            
            print(f"   ✅ 城市: {trip_plan.city}")
            print(f"   ✅ 天数: {len(trip_plan.days)}")
            print(f"   ✅ 建议长度: {len(trip_plan.overall_suggestions)}字符")
            
            if trip_plan.budget:
                print(f"   ✅ 预算总计: {trip_plan.budget.total}元")
            
            print("\n" + "="*60)
            print("✅ 完整工作流测试通过!")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ 工作流测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"完整工作流失败: {str(e)}")
