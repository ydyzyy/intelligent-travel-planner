"""高德地图服务 - 使用REST API直接调用

本模块提供高德地图API的Python封装，包括：
- POI搜索（景点、酒店、餐厅等）
- 天气查询
- 路线规划（步行、驾车、公交）
- 地理编码/逆地理编码
"""

import requests
from typing import List, Dict, Any, Optional
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo


class AmapService:
    """高德地图服务封装类 - 基于REST API"""
    
    def __init__(self):
        """初始化服务"""
        settings = get_settings()
        self.api_key = settings.amap_api_key
        self.base_url = "https://restapi.amap.com/v3"
        
        if not self.api_key:
            raise ValueError("高德地图API Key未配置")
    
    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """
        搜索POI（兴趣点）
        
        Args:
            keywords: 搜索关键词（如"故宫"、"酒店"）
            city: 城市名称
            citylimit: 是否限制在城市范围内
            
        Returns:
            POI信息列表
        """
        try:
            url = f"{self.base_url}/place/text"
            params = {
                "keywords": keywords,
                "city": city,
                "citylimit": "true" if citylimit else "false",
                "key": self.api_key,
                "output": "json",
                "offset": 20,  # 每页数量
                "page": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                print(f"❌ POI搜索失败: {data.get('info', '未知错误')}")
                return []
            
            pois = data.get("pois", [])
            result = []
            
            for poi in pois[:10]:  # 最多返回10个
                try:
                    location_str = poi.get("location", "0,0")
                    lng, lat = location_str.split(",")
                    
                    # 处理tel字段，可能是列表或字符串
                    tel_value = poi.get("tel", "")
                    if isinstance(tel_value, list):
                        tel_value = tel_value[0] if tel_value else ""
                    
                    poi_info = POIInfo(
                        id=poi.get("id", ""),  # 添加id字段
                        name=poi.get("name", ""),
                        type=poi.get("typename", ""),
                        address=poi.get("address", ""),
                        location=Location(
                            longitude=float(lng),
                            latitude=float(lat)
                        ),
                        tel=tel_value if tel_value else None
                    )
                    result.append(poi_info)
                except Exception as e:
                    print(f"⚠️  解析POI数据失败: {e}")
                    continue
            
            print(f"✅ POI搜索成功: 找到{len(result)}个结果")
            return result
            
        except Exception as e:
            print(f"❌ POI搜索异常: {str(e)}")
            return []
    
    def search_poi_nearby(self, keywords: str, location: Location, radius: int = 3000) -> List[POIInfo]:
        """
        在指定位置附近搜索POI
        
        Args:
            keywords: 搜索关键词（如"酒店"、"餐厅"）
            location: 中心位置（经纬度）
            radius: 搜索半径（米），默认3000米
            
        Returns:
            POI信息列表
        """
        try:
            url = f"{self.base_url}/place/around"
            params = {
                "keywords": keywords,
                "location": f"{location.longitude},{location.latitude}",
                "radius": str(radius),
                "key": self.api_key,
                "output": "json",
                "offset": 20,
                "page": 1,
                "sortrule": "distance"  # 按距离排序
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                print(f"❌ 附近POI搜索失败: {data.get('info', '未知错误')}")
                return []
            
            pois = data.get("pois", [])
            result = []
            
            for poi in pois[:10]:  # 最多返回10个
                try:
                    location_str = poi.get("location", "0,0")
                    lng, lat = location_str.split(",")
                    
                    # 处理tel字段
                    tel_value = poi.get("tel", "")
                    if isinstance(tel_value, list):
                        tel_value = tel_value[0] if tel_value else ""
                    
                    poi_info = POIInfo(
                        id=poi.get("id", ""),
                        name=poi.get("name", ""),
                        type=poi.get("typename", ""),
                        address=poi.get("address", ""),
                        location=Location(
                            longitude=float(lng),
                            latitude=float(lat)
                        ),
                        tel=tel_value if tel_value else None,
                        distance=poi.get("distance", "")  # 高德API返回距离
                    )
                    result.append(poi_info)
                except Exception as e:
                    print(f"⚠️  解析附近POI数据失败: {e}")
                    continue
            
            print(f"✅ 附近POI搜索成功: 找到{len(result)}个结果（半径{radius}米）")
            return result
            
        except Exception as e:
            print(f"❌ 附近POI搜索异常: {str(e)}")
            return []
    
    def get_weather(self, city: str) -> List[WeatherInfo]:
        """
        查询天气
        
        Args:
            city: 城市名称或adcode
            
        Returns:
            天气信息列表
        """
        try:
            url = f"{self.base_url}/weather/weatherInfo"
            params = {
                "city": city,
                "key": self.api_key,
                "output": "json",
                "extensions": "all"  # 获取预报天气
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                print(f"❌ 天气查询失败: {data.get('info', '未知错误')}")
                return []
            
            forecasts = data.get("forecasts", [])
            result = []
            
            for forecast in forecasts:
                city_name = forecast.get("city", "未知城市")
                casts = forecast.get("casts", [])
                print(f"📊 天气数据解析 - 城市: {city_name}, 预报天数: {len(casts)}")
                
                for i, cast in enumerate(casts):
                    print(f"  📅 第{i+1}天原始数据: {cast}")
                    try:
                        weather_info = WeatherInfo(
                            date=cast.get("date", ""),
                            day_weather=cast.get("dayweather", ""),
                            night_weather=cast.get("nightweather", ""),
                            day_temp=cast.get("daytemp", ""),
                            night_temp=cast.get("nighttemp", ""),
                            wind_direction=cast.get("daywind", ""),  # 修复: 使用daywind而不是day_wind
                            wind_power=cast.get("daypower", "")     # 修复: 使用daypower而不是day_power
                        )
                        print(f"  ✅ 解析成功 - 日期: {weather_info.date}, 白天温度: {weather_info.day_temp}, 夜间温度: {weather_info.night_temp}")
                        result.append(weather_info)
                    except Exception as e:
                        print(f"  ❌ 解析天气数据失败: {e}")
                        print(f"  📋 原始数据: {cast}")
                        import traceback
                        traceback.print_exc()
                        continue
            
            print(f"✅ 天气查询成功: {len(result)}天预报")
            return result
            
        except Exception as e:
            print(f"❌ 天气查询异常: {str(e)}")
            return []
    
    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """
        规划路线
        
        Args:
            origin_address: 起点地址
            destination_address: 终点地址
            origin_city: 起点城市
            destination_city: 终点城市
            route_type: 路线类型 (walking/driving/transit)
            
        Returns:
            路线信息字典
        """
        try:
            # 根据路线类型选择API端点
            route_map = {
                "walking": f"{self.base_url}/direction/walking",
                "driving": f"{self.base_url}/direction/driving",
                "transit": f"{self.base_url}/direction/transit/integrated"
            }
            
            url = route_map.get(route_type, route_map["walking"])
            
            # 构建请求参数
            params = {
                "origin": origin_address,
                "destination": destination_address,
                "key": self.api_key,
                "output": "json"
            }
            
            if origin_city:
                params["origin_city"] = origin_city
            if destination_city:
                params["destination_city"] = destination_city
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                print(f"❌ 路线规划失败: {data.get('info', '未知错误')}")
                return {"error": data.get("info", "路线规划失败")}
            
            # 解析路线数据
            route_data = data.get("route", {})
            
            if route_type == "transit":
                # 公交路线
                transits = route_data.get("transits", [])
                if transits:
                    transit = transits[0]
                    distance = transit.get("distance", 0)
                    duration = transit.get("duration", 0)
                    cost = transit.get("cost", 0)
                    
                    return {
                        "distance": int(distance),
                        "duration": int(duration),
                        "cost": float(cost),
                        "steps": len(transit.get("segments", [])),
                        "type": "transit"
                    }
            else:
                # 步行或驾车
                paths = route_data.get("paths", [])
                if paths:
                    path = paths[0]
                    distance = path.get("distance", 0)
                    duration = path.get("duration", 0)
                    
                    return {
                        "distance": int(distance),
                        "duration": int(duration),
                        "steps": len(path.get("steps", [])),
                        "type": route_type
                    }
            
            return {"error": "未找到路线"}
            
        except Exception as e:
            print(f"❌ 路线规划异常: {str(e)}")
            return {"error": str(e)}
    
    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """
        地理编码（地址转坐标）
        
        Args:
            address: 地址字符串
            city: 城市名称
            
        Returns:
            Location对象或None
        """
        try:
            url = f"{self.base_url}/geocode/geo"
            params = {
                "address": address,
                "key": self.api_key,
                "output": "json"
            }
            
            if city:
                params["city"] = city
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                return None
            
            geocodes = data.get("geocodes", [])
            if not geocodes:
                return None
            
            location_str = geocodes[0].get("location", "")
            if location_str:
                lng, lat = location_str.split(",")
                return Location(
                    longitude=float(lng),
                    latitude=float(lat)
                )
            
            return None
            
        except Exception as e:
            print(f"❌ 地理编码失败: {str(e)}")
            return None
    
    def get_poi_detail(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """
        获取POI详情
        
        Args:
            poi_id: POI ID
            
        Returns:
            POI详细信息字典
        """
        try:
            url = f"{self.base_url}/place/detail"
            params = {
                "id": poi_id,
                "key": self.api_key,
                "output": "json"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                return None
            
            pois = data.get("pois", [])
            if pois:
                return pois[0]
            
            return None
            
        except Exception as e:
            print(f"❌ 获取POI详情失败: {str(e)}")
            return None


# 全局单例
_amap_service = None


def get_amap_service() -> AmapService:
    """
    获取高德地图服务实例（单例模式）
    
    Returns:
        AmapService实例
    """
    global _amap_service
    
    if _amap_service is None:
        _amap_service = AmapService()
    
    return _amap_service

