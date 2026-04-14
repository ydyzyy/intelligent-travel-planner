# 后端测试文档

本文档介绍如何运行和管理后端测试。

## 📋 目录结构

```
backend/
├── tests/                  # 测试目录
│   ├── __init__.py        # 测试包初始化
│   ├── conftest.py        # pytest配置和fixtures
│   ├── test_models.py     # 数据模型测试
│   ├── test_services.py   # 服务层测试
│   ├── test_api.py        # API接口测试
│   └── test_agents.py     # Agent测试
├── pytest.ini             # pytest配置文件
├── requirements-test.txt  # 测试依赖
└── run_tests.py           # 测试运行脚本
```

## 🚀 快速开始

### 1. 安装测试依赖

```bash
cd backend
pip install -r requirements-test.txt
```

### 2. 运行所有测试

```bash
# 方法1: 使用pytest直接运行
pytest

# 方法2: 使用测试运行脚本
python run_tests.py
```

### 3. 运行特定测试文件

```bash
# 运行数据模型测试
pytest tests/test_models.py

# 运行API测试
pytest tests/test_api.py

# 使用脚本运行
python run_tests.py tests/test_models.py
```

### 4. 生成覆盖率报告

```bash
# 生成HTML和终端覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term-missing

# 或使用脚本
python run_tests.py coverage
```

覆盖率报告将生成在 `htmlcov/` 目录中，打开 `htmlcov/index.html` 查看详细信息。

## 📝 测试分类

### 单元测试 (Unit Tests)

- **test_models.py**: 测试Pydantic数据模型
  - Location, Attraction, Meal, Hotel
  - DayPlan, TripPlan, WeatherInfo, Budget
  - TripRequest, POISearchRequest, RouteRequest

- **test_services.py**: 测试服务层（使用mock）
  - Config配置测试
  - LLM服务测试
  - AmapService高德地图服务测试
  - MCP工具测试

- **test_agents.py**: 测试Agent逻辑
  - 提示词验证
  - MultiAgentTripPlanner初始化和方法测试
  - 单例模式测试

### 集成测试 (Integration Tests)

- **test_api.py**: 测试FastAPI端点
  - 健康检查接口
  - 旅行规划接口
  - 错误处理测试
  - 完整工作流程测试

## 🎯 使用pytest标记

可以使用标记来运行特定类型的测试：

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"
```

## 🔧 Fixtures说明

在 `conftest.py` 中定义了常用的测试fixtures：

- `client`: FastAPI测试客户端
- `sample_trip_request`: 示例旅行请求
- `sample_location`: 示例位置坐标
- `sample_attraction`: 示例景点
- `sample_meal`: 示例餐饮
- `sample_day_plan`: 示例日计划
- `sample_trip_plan`: 示例旅行计划
- `mock_env_vars`: 模拟环境变量

使用示例：

```python
def test_example(sample_trip_request, client):
    """使用fixtures的测试函数"""
    response = client.post("/api/trip/plan", json=sample_trip_request.dict())
    assert response.status_code == 200
```

## 📊 测试最佳实践

### 1. Mock外部依赖

对于涉及外部API的测试（如LLM、高德地图），使用mock：

```python
from unittest.mock import Mock, patch

@patch('app.services.amap_service.get_amap_mcp_tool')
def test_search_poi(mock_get_mcp_tool):
    mock_mcp = Mock()
    mock_mcp.run.return_value = '{"pois": []}'
    mock_get_mcp_tool.return_value = mock_mcp
    
    service = AmapService()
    result = service.search_poi("故宫", "北京")
    
    assert isinstance(result, list)
```

### 2. 测试边界条件

```python
def test_invalid_travel_days():
    """测试无效的天数"""
    with pytest.raises(Exception):
        TripRequest(
            city="北京",
            start_date="2025-06-01",
            end_date="2025-06-03",
            travel_days=0,  # 无效值
            transportation="公共交通",
            accommodation="酒店"
        )
```

### 3. 测试错误处理

```python
def test_api_error_handling(client):
    """测试API错误处理"""
    invalid_request = {"city": "北京"}  # 缺少必填字段
    response = client.post("/api/trip/plan", json=invalid_request)
    assert response.status_code == 422
```

## 🐛 调试测试

### 查看详细输出

```bash
pytest -v -s
```

### 只显示失败的测试

```bash
pytest -x  # 第一个失败就停止
pytest --tb=short  # 简短的回溯信息
```

### 运行单个测试函数

```bash
pytest tests/test_models.py::TestLocation::test_create_location -v
```

## 🔄 CI/CD集成

可以将测试集成到CI/CD流程中：

```yaml
# .github/workflows/test.yml 示例
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📈 测试覆盖率目标

- **数据模型**: 90%+
- **服务层**: 80%+
- **API路由**: 85%+
- **Agent逻辑**: 75%+

## ⚠️ 注意事项

1. **环境变量**: 测试时会使用mock的环境变量，不会影响实际配置
2. **外部API**: 所有外部API调用都被mock，不会真实调用
3. **数据库**: 当前项目不使用数据库，无需特殊配置
4. **并发测试**: 如需并发测试，可使用 `pytest-xdist` 插件

## 🆘 常见问题

### Q: 测试导入错误？
A: 确保在backend目录下运行测试，或设置PYTHONPATH：
```bash
export PYTHONPATH=${PYTHONPATH}:$(pwd)
```

### Q: Mock不生效？
A: 确保mock的路径正确，应该mock使用的地方而非定义的地方。

### Q: 如何添加新测试？
A: 
1. 在tests目录下创建新的test_*.py文件
2. 编写测试类和方法（以Test和test_开头）
3. 使用现有的fixtures或创建新的fixtures
4. 运行测试验证

## 📚 参考资料

- [pytest官方文档](https://docs.pytest.org/)
- [FastAPI测试指南](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock文档](https://docs.python.org/3/library/unittest.mock.html)
