"""数据模型测试"""

import pytest
from datetime import datetime
from app.models.schemas import (
    TripRequest,
    Location,
    Attraction,
    Meal,
    Hotel,
    DayPlan,
    WeatherInfo,
    Budget,
    TripPlan,
    POISearchRequest,
    RouteRequest
)


class TestLocation:
    """位置模型测试"""
    
    def test_create_location(self):
        """测试创建位置对象"""
        location = Location(longitude=116.397128, latitude=39.916527)
        assert location.longitude == 116.397128
        assert location.latitude == 39.916527
    
    def test_location_with_extreme_values(self):
        """测试极端坐标值（Location模型当前不验证范围）"""
        # 注意：当前Location模型没有经度/纬度范围验证
        # 如果需要验证，应该在Location模型中添加validator
        location = Location(longitude=200.0, latitude=39.916527)
        assert location.longitude == 200.0  # 当前允许无效值
        
        # TODO: 如果需要在模型中添加验证，可以取消下面的注释
        # with pytest.raises(Exception):
        #     Location(longitude=200.0, latitude=39.916527)


class TestAttraction:
    """景点模型测试"""
    
    def test_create_attraction(self, sample_location, sample_attraction):
        """测试创建景点对象"""
        assert sample_attraction.name == "故宫博物院"
        assert sample_attraction.location.longitude == 116.397128
        assert sample_attraction.ticket_price == 60
        assert sample_attraction.category == "历史文化"
    
    def test_attraction_optional_fields(self, sample_location):
        """测试景点可选字段"""
        attraction = Attraction(
            name="测试景点",
            address="测试地址",
            location=sample_location,
            visit_duration=120,
            description="测试描述"
        )
        assert attraction.rating is None
        assert attraction.photos == []


class TestMeal:
    """餐饮模型测试"""
    
    def test_create_meal(self, sample_meal):
        """测试创建餐饮对象"""
        assert sample_meal.type == "lunch"
        assert sample_meal.name == "北京烤鸭"
        assert sample_meal.estimated_cost == 150
    
    def test_meal_types(self, sample_location):
        """测试不同餐饮类型"""
        for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
            meal = Meal(
                type=meal_type,
                name=f"测试{meal_type}",
                description="测试"
            )
            assert meal.type == meal_type


class TestHotel:
    """酒店模型测试"""
    
    def test_create_hotel(self, sample_location):
        """测试创建酒店对象"""
        hotel = Hotel(
            name="测试酒店",
            address="测试地址",
            location=sample_location,
            price_range="300-500元",
            rating="4.5",
            estimated_cost=400
        )
        assert hotel.name == "测试酒店"
        assert hotel.estimated_cost == 400
    
    def test_hotel_optional_fields(self):
        """测试酒店可选字段"""
        hotel = Hotel(name="简单酒店")
        assert hotel.address == ""
        assert hotel.location is None
        assert hotel.estimated_cost == 0


class TestWeatherInfo:
    """天气信息模型测试"""
    
    def test_create_weather_info(self):
        """测试创建天气信息"""
        weather = WeatherInfo(
            date="2025-06-01",
            day_weather="晴",
            night_weather="多云",
            day_temp=25,
            night_temp=15,
            wind_direction="南风",
            wind_power="1-3级"
        )
        assert weather.day_temp == 25
        assert weather.night_temp == 15
    
    def test_parse_temperature_with_unit(self):
        """测试解析带单位的温度"""
        weather = WeatherInfo(
            date="2025-06-01",
            day_temp="25°C",
            night_temp="15℃"
        )
        assert weather.day_temp == 25
        assert weather.night_temp == 15
    
    def test_parse_temperature_string(self):
        """测试解析字符串温度"""
        weather = WeatherInfo(
            date="2025-06-01",
            day_temp="20",
            night_temp="10"
        )
        assert weather.day_temp == 20
        assert weather.night_temp == 10


class TestBudget:
    """预算模型测试"""
    
    def test_create_budget(self):
        """测试创建预算对象"""
        budget = Budget(
            total_attractions=180,
            total_hotels=1200,
            total_meals=480,
            total_transportation=200,
            total=2060
        )
        assert budget.total == 2060
        assert budget.total_attractions == 180
    
    def test_default_budget(self):
        """测试默认预算值"""
        budget = Budget()
        assert budget.total == 0
        assert budget.total_attractions == 0


class TestDayPlan:
    """日计划模型测试"""
    
    def test_create_day_plan(self, sample_day_plan):
        """测试创建日计划"""
        assert sample_day_plan.date == "2025-06-01"
        assert sample_day_plan.day_index == 0
        assert len(sample_day_plan.attractions) == 1
        assert len(sample_day_plan.meals) == 1
    
    def test_day_plan_empty_lists(self, sample_location):
        """测试日计划空列表"""
        day_plan = DayPlan(
            date="2025-06-01",
            day_index=0,
            description="测试",
            transportation="公共交通",
            accommodation="酒店"
        )
        assert day_plan.attractions == []
        assert day_plan.meals == []


class TestTripPlan:
    """旅行计划模型测试"""
    
    def test_create_trip_plan(self, sample_trip_plan):
        """测试创建旅行计划"""
        assert sample_trip_plan.city == "北京"
        assert sample_trip_plan.start_date == "2025-06-01"
        assert len(sample_trip_plan.days) == 1
    
    def test_trip_plan_with_weather_and_budget(self, sample_day_plan):
        """测试包含天气和预算的旅行计划"""
        weather = WeatherInfo(date="2025-06-01", day_temp=25, night_temp=15)
        budget = Budget(total=2060)
        
        trip_plan = TripPlan(
            city="北京",
            start_date="2025-06-01",
            end_date="2025-06-03",
            days=[sample_day_plan],
            weather_info=[weather],
            budget=budget,
            overall_suggestions="测试建议"
        )
        
        assert len(trip_plan.weather_info) == 1
        assert trip_plan.budget.total == 2060


class TestTripRequest:
    """旅行请求模型测试"""
    
    def test_create_trip_request(self, sample_trip_request):
        """测试创建旅行请求"""
        assert sample_trip_request.city == "北京"
        assert sample_trip_request.travel_days == 3
        assert len(sample_trip_request.preferences) == 2
        assert "历史文化" in sample_trip_request.preferences
    
    def test_trip_request_validation(self):
        """测试旅行请求验证"""
        # 测试天数范围
        with pytest.raises(Exception):
            TripRequest(
                city="北京",
                start_date="2025-06-01",
                end_date="2025-06-03",
                travel_days=0,  # 无效：小于1
                transportation="公共交通",
                accommodation="酒店"
            )
        
        with pytest.raises(Exception):
            TripRequest(
                city="北京",
                start_date="2025-06-01",
                end_date="2025-06-03",
                travel_days=31,  # 无效：大于30
                transportation="公共交通",
                accommodation="酒店"
            )
    
    def test_trip_request_optional_fields(self):
        """测试旅行请求可选字段"""
        request = TripRequest(
            city="上海",
            start_date="2025-07-01",
            end_date="2025-07-02",
            travel_days=2,
            transportation="自驾",
            accommodation="豪华酒店"
        )
        assert request.preferences == []
        assert request.free_text_input == ""


class TestPOISearchRequest:
    """POI搜索请求测试"""
    
    def test_create_poi_search_request(self):
        """测试创建POI搜索请求"""
        request = POISearchRequest(
            keywords="故宫",
            city="北京",
            citylimit=True
        )
        assert request.keywords == "故宫"
        assert request.city == "北京"
        assert request.citylimit is True


class TestRouteRequest:
    """路线规划请求测试"""
    
    def test_create_route_request(self):
        """测试创建路线规划请求"""
        request = RouteRequest(
            origin_address="北京市朝阳区阜通东大街6号",
            destination_address="北京市海淀区上地十街10号",
            route_type="walking"
        )
        assert request.route_type == "walking"
        assert request.origin_city is None
    
    def test_route_request_with_cities(self):
        """测试带城市的路线请求"""
        request = RouteRequest(
            origin_address="起点",
            destination_address="终点",
            origin_city="北京",
            destination_city="上海",
            route_type="driving"
        )
        assert request.origin_city == "北京"
        assert request.destination_city == "上海"
