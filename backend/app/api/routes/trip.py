"""旅行规划API路由"""

from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """
    生成旅行计划

    Args:
        request: 旅行请求参数

    Returns:
        旅行计划响应
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"{'='*60}\n")

        # 获取Agent实例
        print("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        # 生成旅行计划
        print("🚀 开始生成旅行计划...")
        trip_plan = agent.plan_trip(request)

        # 在终端打印完整的行程计划供开发者对照
        print(f"\n{'='*70}")
        print(f"✨ 旅行计划生成完成!")
        print(f"{'='*70}")
        print(f"📍 城市: {trip_plan.city}")
        print(f"📅 日期: {trip_plan.start_date} 至 {trip_plan.end_date}")
        print(f"📝 建议: {trip_plan.overall_suggestions}")
        print(f"\n📊 每日行程概览:")
        for i, day in enumerate(trip_plan.days, 1):
            print(f"\n  ┌─ 第{i}天 ({day.date})")
            print(f"  │ 描述: {day.description}")
            print(f"  │ 交通: {day.transportation}")
            print(f"  │ 住宿: {day.accommodation}")
            print(f"  │ 景点 ({len(day.attractions)}个):")
            for j, attr in enumerate(day.attractions, 1):
                print(f"  │   {j}. {attr.name} - {attr.address}")
                print(f"  │      时长: {attr.visit_duration}分钟 | 描述: {attr.description[:50]}...")
            if day.meals:
                print(f"  │ 餐饮:")
                for meal in day.meals:
                    print(f"  │   - {meal.type}: {meal.name}")
            print(f"  └─{'─' * 60}")
        
        if trip_plan.budget:
            print(f"\n💰 预算明细:")
            print(f"   景点门票: ¥{trip_plan.budget.total_attractions}")
            print(f"   酒店住宿: ¥{trip_plan.budget.total_hotels}")
            print(f"   餐饮费用: ¥{trip_plan.budget.total_meals}")
            print(f"   交通费用: ¥{trip_plan.budget.total_transportation}")
            print(f"   总计: ¥{trip_plan.budget.total}")
        
        if trip_plan.weather_info:
            print(f"\n🌤️ 天气预报:")
            for weather in trip_plan.weather_info:
                print(f"   {weather.date}: {weather.day_weather} {weather.day_temp}°C / {weather.night_weather} {weather.night_temp}°C")
        
        print(f"\n{'='*70}")
        print(f"✅ 准备返回响应给前端...\n")

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )

    except Exception as e:
        print(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()
        
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": "多智能体旅行规划系统",
            "components": {
                "attraction_agent": "景点搜索专家",
                "weather_agent": "天气查询专家", 
                "hotel_agent": "酒店推荐专家",
                "planner_agent": "行程规划专家"
            },
            "tools_count": 0,  # LangChain版本不使用工具计数
            "llm_provider": "OpenAI兼容" if hasattr(agent, 'llm') else "unknown",
            "llm_model": getattr(agent.llm, 'model_name', getattr(agent.llm, 'model', 'unknown')) if hasattr(agent, 'llm') else "unknown"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )

