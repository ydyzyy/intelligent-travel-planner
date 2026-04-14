"""多智能体旅行规划系统 - 使用REST API版本

本模块实现基于LangChain的多智能体旅行规划系统，直接使用高德地图REST API，
不再依赖MCP工具层。
"""

import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..services.llm_service import get_llm
from ..services.amap_service import get_amap_service
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from ..config import get_settings


# ============ Agent提示词 ============

ATTRACTION_AGENT_PROMPT = """你是景点搜索专家。你的任务是根据城市和用户偏好推荐合适的景点。

请根据以下信息推荐景点：
- 城市：{city}
- 偏好：{preferences}
- 天数：{days}天

请推荐适合该城市的景点，包括：
1. 景点名称
2. 景点类型（历史文化、自然风光、娱乐休闲等）
3. 建议游览时长
4. 门票价格范围
5. 简要介绍

请以JSON格式返回，包含一个attractions数组。
"""

WEATHER_AGENT_PROMPT = """你是天气查询专家。你将收到真实的天气数据，请分析并提供穿衣和出行建议。

天气数据：
{weather_data}

请提供：
1. 每日天气概况
2. 穿衣建议
3. 出行注意事项
"""

HOTEL_AGENT_PROMPT = """你是酒店推荐专家。你将收到真实的酒店搜索数据，请分析并推荐合适的酒店。

酒店数据：
{hotel_data}
城市：{city}
住宿偏好：{accommodation}

请推荐2-3家合适的酒店，说明推荐理由。
"""

PLANNER_AGENT_PROMPT = """你是行程规划专家。你的任务是根据景点、天气、酒店信息，生成详细的旅行计划。

**重要原则**:
1. 酒店选择必须靠近景点: 选择距离主要景点3公里范围内的酒店,避免每天长途奔波
2. 每天的景点安排要集中: 同一天的景点应该在相近区域,减少交通时间
3. 餐厅选择也要考虑位置: 优先选择景点附近的餐厅

请严格按照以下JSON格式返回旅行计划：
```json
{{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {{
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {{
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {{"longitude": 116.397128, "latitude": 39.916527}},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      }},
      "attractions": [
        {{
          "name": "景点名称",
          "address": "景点地址",
          "location": {{"longitude": 116.397128, "latitude": 39.916527}},
          "visit_duration": 120,
          "ticket_price": 60,
          "description": "景点介绍",
          "category": "景点类型"
        }}
      ],
      "meals": [
        {{
          "name": "餐厅名称",
          "address": "餐厅地址",
          "location": {{"longitude": 116.397128, "latitude": 39.916527}},
          "type": "breakfast/lunch/dinner/snack",
          "meal_type": "早餐/午餐/晚餐（可选）",
          "estimated_cost": 50,
          "description": "餐厅介绍"
        }}
      ]
    }}
  ],
  "weather_info": [
    {{
      "date": "YYYY-MM-DD",
      "day_weather": "白天天气",
      "night_weather": "夜间天气",
      "day_temp": 25,
      "night_temp": 18,
      "wind_direction": "风向",
      "wind_power": "风力"
    }}
  ],
  "overall_suggestions": "总体建议",
  "budget": {{
    "total_attractions": 200,
    "total_meals": 500,
    "total_transportation": 150,
    "total_hotels": 800,
    "total": 1650
  }}
}}
```

**重要要求:**
1. 必须返回有效的JSON格式
2. 所有字段都必须存在
3. 坐标必须是真实的经纬度数值
4. 价格单位是元
5. 时间单位是分钟
6. 天气温度必须是数字类型
"""


class MultiAgentTripPlanner:
    """多智能体旅行规划系统 - REST API版本"""

    def __init__(self):
        """初始化多智能体系统"""
        print("🔄 开始初始化多智能体旅行规划系统...")

        try:
            settings = get_settings()
            self.llm = get_llm()
            
            # 初始化高德地图服务
            print("  - 初始化高德地图服务...")
            self.amap_service = get_amap_service()
            print(f"✅ 高德地图服务初始化成功")

            print(f"✅ 多智能体系统初始化成功")
            # 安全地打印LLM信息
            try:
                print(f"   LLM提供商: OpenAI兼容")
                if hasattr(self.llm, 'model_name'):
                    print(f"   LLM模型: {self.llm.model_name}")
                elif hasattr(self.llm, 'model'):
                    print(f"   LLM模型: {self.llm.model}")
            except Exception as e:
                print(f"   注意: 无法获取LLM详细信息 - {e}")

        except Exception as e:
            print(f"❌ 多智能体系统初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        使用多智能体协作生成旅行计划

        Args:
            request: 旅行请求

        Returns:
            旅行计划
        """
        try:
            import time
            start_time = time.time()
            
            print(f"\n{'='*60}")
            print(f"🚀 开始多智能体协作规划旅行...")
            print(f"目的地: {request.city}")
            print(f"日期: {request.start_date} 至 {request.end_date}")
            print(f"天数: {request.travel_days}天")
            print(f"偏好: {', '.join(request.preferences) if request.preferences else '无'}")
            print(f"{'='*60}\n")

            # 步骤1: 直接使用AmapService搜索景点
            print("📍 步骤1: 搜索景点...")
            step1_start = time.time()
            preferences_str = ", ".join(request.preferences) if request.preferences else "热门景点"
            pois = self.amap_service.search_poi(preferences_str, request.city)
            attraction_data = self._format_pois_for_llm(pois)
            step1_time = time.time() - step1_start
            print(f"   找到{len(pois)}个景点 (耗时: {step1_time:.2f}秒)\n")

            # 步骤2: 直接使用AmapService查询天气
            print("🌤️  步骤2: 查询天气...")
            step2_start = time.time()
            weather_infos = self.amap_service.get_weather(request.city)
            weather_data = self._format_weather_for_llm(weather_infos)
            step2_time = time.time() - step2_start
            print(f"   获取{len(weather_infos)}天天气预报 (耗时: {step2_time:.2f}秒)\n")

            # 步骤3: 直接使用AmapService搜索酒店
            print("🏨 步骤3: 搜索酒店...")
            step3_start = time.time()
            # 优化: 先获取所有景点位置,然后在景点附近搜索酒店
            attraction_locations = []
            for poi in pois[:3]:  # 取前3个主要景点
                if hasattr(poi, 'location') and poi.location:
                    attraction_locations.append(poi.location)
            
            # 如果有景点位置,在景点附近搜索酒店
            if attraction_locations:
                # 使用第一个景点位置作为中心搜索酒店
                center_poi = pois[0] if pois else None
                if center_poi and hasattr(center_poi, 'location'):
                    print(f"   以 {center_poi.name} 为中心搜索酒店...")
                    # 搜索景点附近的酒店
                    hotels = self.amap_service.search_poi_nearby(
                        keywords="酒店",
                        location=center_poi.location,
                        radius=3000  # 3公里范围内
                    )
                else:
                    hotels = self.amap_service.search_poi("酒店", request.city)
            else:
                # 如果没有景点位置,使用城市搜索
                hotels = self.amap_service.search_poi("酒店", request.city)
            
            hotel_data = self._format_pois_for_llm(hotels[:5])  # 只取前5个
            step3_time = time.time() - step3_start
            print(f"   找到{len(hotels)}个酒店 (耗时: {step3_time:.2f}秒)\n")

            # 步骤4: 构建Agent查询并生成计划
            print("📋 步骤4: 生成行程计划...")
            step4_start = time.time()
            planner_query = self._build_planner_query(request, attraction_data, weather_data, hotel_data)
            
            # 使用LangChain运行提示词
            output_parser = StrOutputParser()
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", PLANNER_AGENT_PROMPT),
                ("human", "{input}")
            ])
            chain = prompt_template | self.llm | output_parser
            planner_response = chain.invoke({"input": planner_query})
            
            step4_time = time.time() - step4_start
            print(f"   LLM响应长度: {len(planner_response)}字符 (耗时: {step4_time:.2f}秒)\n")

            # 解析最终计划
            trip_plan = self._parse_response(planner_response, request)

            total_time = time.time() - start_time
            print(f"\n{'='*60}")
            print(f"✅ 旅行计划生成完成!")
            print(f"📊 性能统计:")
            print(f"   - 景点搜索: {step1_time:.2f}秒")
            print(f"   - 天气查询: {step2_time:.2f}秒")
            print(f"   - 酒店搜索: {step3_time:.2f}秒")
            print(f"   - LLM生成: {step4_time:.2f}秒")
            print(f"   - 总耗时: {total_time:.2f}秒")
            print(f"{'='*60}\n")

            # 添加性能数据到trip_plan
            trip_plan.performance = {
                "poi_search": round(step1_time, 2),
                "weather_query": round(step2_time, 2),
                "hotel_search": round(step3_time, 2),
                "llm_generation": round(step4_time, 2),
                "total_time": round(total_time, 2)
            }

            return trip_plan

        except Exception as e:
            print(f"❌ 生成旅行计划失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_plan(request)
    
    def _format_pois_for_llm(self, pois: List) -> str:
        """格式化POI数据给LLM"""
        if not pois:
            return "未找到相关POI"
        
        lines = []
        for poi in pois:
            lines.append(f"- {poi.name} ({poi.type})")
            lines.append(f"  地址: {poi.address}")
            if hasattr(poi, 'rating') and poi.rating:
                lines.append(f"  评分: {poi.rating}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_weather_for_llm(self, weather_infos: List[WeatherInfo]) -> str:
        """格式化天气数据给LLM"""
        if not weather_infos:
            return "未获取到天气数据"
        
        lines = []
        for w in weather_infos:
            lines.append(f"日期: {w.date}")
            lines.append(f"  白天: {w.day_weather}, 温度: {w.day_temp}°C")
            lines.append(f"  夜间: {w.night_weather}, 温度: {w.night_temp}°C")
            if hasattr(w, 'wind_direction') and w.wind_direction:
                lines.append(f"  风向: {w.wind_direction}")
            if hasattr(w, 'wind_power') and w.wind_power:
                lines.append(f"  风力: {w.wind_power}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _build_planner_query(self, request: TripRequest, attraction_data: str, 
                            weather_data: str, hotel_data: str) -> str:
        """构建行程规划查询"""
        query = f"""请为以下旅行需求生成详细的行程计划：

**旅行信息:**
- 城市: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.travel_days}天
- 交通偏好: {request.transportation or '公共交通'}
- 住宿偏好: {request.accommodation or '经济型酒店'}
- 用户偏好: {', '.join(request.preferences) if request.preferences else '无特殊偏好'}

**可用景点:**
{attraction_data}

**天气预报:**
{weather_data}

**可用酒店:**
{hotel_data}

请根据以上信息，生成符合JSON格式的完整旅行计划。确保：
1. 每天的行程安排合理，不要过于紧凑
2. 考虑天气情况，雨天安排室内活动
3. 餐厅选择要符合当地特色
4. 预算估算要合理
5. 返回的必须是有效的JSON格式
"""
        return query
    
    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """解析LLM响应为TripPlan对象"""
        try:
            # 尝试提取JSON
            json_str = response
            
            # 如果响应包含代码块，提取其中的JSON
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end > start:
                    json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end > start:
                    json_str = response[start:end].strip()
            
            # 解析JSON
            data = json.loads(json_str)
            
            # 构建TripPlan对象
            days = []
            for day_data in data.get("days", []):
                attractions = []
                for attr in day_data.get("attractions", []):
                    location_data = attr.get("location", {})
                    attractions.append(Attraction(
                        name=attr.get("name", ""),
                        address=attr.get("address", ""),
                        location=Location(
                            longitude=location_data.get("longitude", 0),
                            latitude=location_data.get("latitude", 0)
                        ),
                        visit_duration=attr.get("visit_duration", 120),
                        ticket_price=attr.get("ticket_price", 0),
                        description=attr.get("description", ""),
                        category=attr.get("category", "")
                    ))
                
                meals = []
                for meal in day_data.get("meals", []):
                    location_data = meal.get("location", {})
                    meals.append(Meal(
                        type=meal.get("type"),  # 优先使用type字段
                        meal_type=meal.get("meal_type", "午餐"),  # 兼容meal_type字段
                        name=meal.get("name", ""),
                        address=meal.get("address", ""),
                        location=Location(
                            longitude=location_data.get("longitude", 0),
                            latitude=location_data.get("latitude", 0)
                        ),
                        estimated_cost=meal.get("estimated_cost", 50),
                        description=meal.get("description", "")
                    ))
                
                hotel_data = day_data.get("hotel", {})
                hotel_location = hotel_data.get("location", {})
                hotel = Hotel(
                    name=hotel_data.get("name", ""),
                    address=hotel_data.get("address", ""),
                    location=Location(
                        longitude=hotel_location.get("longitude", 0),
                        latitude=hotel_location.get("latitude", 0)
                    ),
                    price_range=hotel_data.get("price_range", ""),
                    rating=hotel_data.get("rating", ""),
                    distance=hotel_data.get("distance", ""),
                    type=hotel_data.get("type", ""),
                    estimated_cost=hotel_data.get("estimated_cost", 0)
                ) if hotel_data.get("name") else None
                
                days.append(DayPlan(
                    date=day_data.get("date", ""),
                    day_index=day_data.get("day_index", 0),
                    description=day_data.get("description", ""),
                    transportation=day_data.get("transportation", ""),
                    accommodation=day_data.get("accommodation", ""),
                    hotel=hotel,
                    attractions=attractions,
                    meals=meals
                ))
            
            # 解析天气信息
            weather_info = []
            for w in data.get("weather_info", []):
                weather_info.append(WeatherInfo(
                    date=w.get("date", ""),
                    day_weather=w.get("day_weather", ""),
                    night_weather=w.get("night_weather", ""),
                    day_temp=w.get("day_temp", ""),      # ✅ 修复: 使用day_temp
                    night_temp=w.get("night_temp", ""),  # ✅ 修复: 使用night_temp
                    wind_direction=w.get("wind_direction", ""),
                    wind_power=w.get("wind_power", "")
                ))
                print(f"  🌡️ 解析天气 - 日期: {w.get('date')}, 白天温度: {w.get('day_temp')}, 夜间温度: {w.get('night_temp')}")
            
            # 解析预算
            budget_data = data.get("budget", {})
            from ..models.schemas import Budget
            budget = Budget(
                total_attractions=budget_data.get("attractions", budget_data.get("total_attractions", 0)),
                total_meals=budget_data.get("meals", budget_data.get("total_meals", 0)),
                total_transportation=budget_data.get("transportation", budget_data.get("total_transportation", 0)),
                total_hotels=budget_data.get("accommodation", budget_data.get("total_hotels", 0)),
                total=budget_data.get("total", 0)
            )
            
            return TripPlan(
                city=data.get("city", request.city),
                start_date=data.get("start_date", request.start_date),
                end_date=data.get("end_date", request.end_date),
                days=days,
                overall_suggestions=data.get("overall_suggestions", ""),
                weather_info=weather_info,
                budget=budget
            )
            
        except Exception as e:
            print(f"⚠️  JSON解析失败: {e}")
            print(f"   原始响应: {response[:500]}...")
            return self._create_fallback_plan(request)
    
    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """创建备用计划（当LLM失败时）"""
        from datetime import datetime, timedelta
        
        days = []
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)
            days.append(DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i+1}天在{request.city}的行程",
                transportation=request.transportation or "公共交通",
                accommodation=request.accommodation or "酒店",
                hotel=None,
                attractions=[],
                meals=[]
            ))
        
        from ..models.schemas import Budget
        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            overall_suggestions=f"抱歉，由于技术问题，无法生成详细行程。建议您在{request.city}探索当地的著名景点和美食。",
            weather_info=[],
            budget=Budget()
        )


# 全局单例
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """
    获取旅行规划Agent实例（单例模式）
    
    Returns:
        MultiAgentTripPlanner实例
    """
    global _multi_agent_planner
    
    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()
    
    return _multi_agent_planner
