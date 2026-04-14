# 智能旅行助手 🌍✈️

基于LangChain框架构建的智能旅行规划助手,集成高德地图REST API服务,提供个性化的旅行计划生成。

## ✨ 功能特点

- 🤖 **AI驱动的旅行规划**: 基于LangChain的自定义Agent,智能生成详细的多日旅程
- 🗺️ **高德地图集成**: 通过REST API接入高德地图服务,支持景点搜索、路线规划、天气查询
- 🧠 **智能工具调用**: Agent自动调用高德地图工具,获取实时POI、路线和天气信息
- 🎨 **现代化前端**: Vue3 + TypeScript + Vite,响应式设计,流畅的用户体验
- 📱 **完整功能**: 包含住宿、交通、餐饮和景点游览时间推荐

## 🏗️ 技术栈

### 后端
- **框架**: LangChain (自定义Agent)
- **API**: FastAPI
- **地图服务**: 高德地图 REST API
- **LLM**: 支持多种LLM提供商(OpenAI, DeepSeek等)

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design Vue
- **地图服务**: 高德地图 JavaScript API
- **HTTP客户端**: Axios

## 📊 项目结构

```
intelligent-travel-planner/
├── start.py                 # 一键启动脚本（主入口）
├── start.bat                # Windows启动脚本
├── start.sh                 # Linux/Mac启动脚本
├── 一键启动使用指南.md      # 详细使用说明
│
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── agents/         # 智能体层
│   │   ├── api/            # API路由
│   │   ├── services/       # 服务层
│   │   └── models/         # 数据模型
│   ├── tests/              # 测试套件
│   ├── requirements.txt    # Python依赖
│   └── .env                # 环境变量
│
└── frontend/               # 前端应用
    ├── src/
    │   ├── views/          # 页面组件
    │   ├── services/       # API服务
    │   └── types/          # 类型定义
    ├── package.json        # Node.js依赖
    └── .env                # 环境变量
```

## 🚀 快速开始

### 🚀 一键启动（推荐）

#### Windows用户

**直接双击运行**:
```
start.bat
```

或者在命令行中运行:
```bash
python start.py
```

#### Linux/Mac用户

```bash
chmod +x start.sh
./start.sh
```

或者:
```bash
python3 start.py
```

#### 启动流程

```
双击 start.bat / 运行 ./start.sh
   ↓
自动检查环境（Python、Node.js）
   ↓
自动安装依赖（如需要）
   ↓
并行启动后端和前端
   ↓
等待服务就绪（15-30秒）
   ↓
自动打开浏览器
   ↓
开始使用！
```

---

### 📋 系统要求

#### 必需软件

- **Python**: 3.10+ 
- **Node.js**: 16+
- **npm**: 随Node.js自动安装

#### API密钥配置

在使用前，需要配置以下API密钥：

1. **后端配置** (`backend/.env`)
   ```bash
   # 复制示例文件
   cd backend
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   
   # 编辑.env文件，填入:
   AMAP_API_KEY=你的高德地图API密钥
   LLM_API_KEY=你的LLM API密钥
   LLM_BASE_URL=https://api.openai.com/v1  # 或其他兼容API
   LLM_MODEL=qwen3.6-plus  # 或gpt-4等
   ```

2. **前端配置** (`frontend/.env`)
   ```bash
   # 复制示例文件
   cd frontend
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   
   # 编辑.env文件，填入:
   VITE_AMAP_JS_API_KEY=你的高德地图JS API密钥
   ```

**获取API密钥**:
- 高德地图: https://lbs.amap.com/
- LLM提供商: OpenAI / DeepSeek / 阿里云等

---

### 🎯 使用方式

#### 方式1: 一键启动（最简单）

```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

**优势**:
- ✅ 全自动，无需手动操作
- ✅ 自动检查环境和依赖
- ✅ 自动打开浏览器
- ✅ 按Ctrl+C优雅退出

#### 方式2: 手动启动

如果需要分别控制后端和前端：

**启动后端**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

**启动前端** (新终端):
```bash
cd frontend
npm install
npm run dev
```

**访问**:
- 前端界面: http://localhost:5173
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

---

## 📝 使用指南

1. 在首页填写旅行信息:
   - 目的地城市
   - 旅行日期和天数
   - 交通方式偏好
   - 住宿偏好
   - 旅行风格标签

2. 点击"生成旅行计划"按钮

3. 系统将:
   - 调用LangChain Agent生成初步计划
   - Agent自动调用高德地图REST API搜索景点
   - Agent获取天气信息和路线规划
   - 整合所有信息生成完整行程

4. 查看结果:
   - 每日详细行程
   - 景点信息与地图标记
   - 交通路线规划
   - 天气预报
   - 餐饮推荐

## 🔧 核心实现

### LangChain Agent集成

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建LLM实例
llm = ChatOpenAI(
    api_key="your_api_key",
    base_url="https://api.openai.com/v1",
    model="qwen3.6-plus"
)

# 创建提示词模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的旅行规划助手..."),
    ("human", "{input}")
])

# 创建处理链
output_parser = StrOutputParser()
chain = prompt_template | llm | output_parser

# 执行推理
response = chain.invoke({"input": "生成广州3日游行程"})
```

### 高德地图REST API调用

Agent可以自动调用以下高德地图REST API:
- `/v3/place/text`: 搜索景点POI
- `/v3/weather/weatherInfo`: 查询天气
- `/v3/direction/walking`: 步行路线规划
- `/v3/direction/driving`: 驾车路线规划
- `/v3/direction/transit`: 公共交通路线规划

## 📄 API文档

启动后端服务后,访问 `http://localhost:8000/docs` 查看完整的API文档。

主要端点:
- `POST /api/trip/plan` - 生成旅行计划
- `GET /api/map/poi` - 搜索POI
- `GET /api/map/weather` - 查询天气
- `POST /api/map/route` - 规划路线

## ⚠️ 常见问题

### 1. 端口被占用

**错误**: `ERROR: [Errno 10048] error while attempting to bind on address`

**解决**:
```bash
# 查找并结束占用端口的进程
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

### 2. 依赖安装失败

**解决**:
```bash
# 手动安装依赖
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

### 3. API密钥未配置

**错误**: `高德地图API Key未配置`

**解决**: 按照上方"API密钥配置"章节设置`.env`文件

### 4. 服务启动超时

**解决**:
- 检查后端日志查看详细错误
- 确认API密钥有效
- 检查网络连接

更多问题请查看 [`一键启动使用指南.md`](一键启动使用指南.md)

---

## 📚 相关文档

- [一键启动使用指南](一键启动使用指南.md) - 详细的启动说明
- [前端优化完成报告](frontend/前端优化完成报告.md) - 前端优化总结

---

## 🎊 开始使用

**只需3步**:

1. **配置API密钥**
   ```bash
   cd backend
   copy .env.example .env
   # 编辑.env填入API密钥
   ```

2. **一键启动**
   ```bash
   # Windows: 双击 start.bat
   # Linux/Mac: ./start.sh
   ```

3. **开始规划旅行**
   - 浏览器自动打开
   - 输入旅行需求
   - 等待AI生成行程
   - 查看详细计划

**就这么简单！** 🎉

---

## 💬 反馈与支持

如有问题或建议，欢迎反馈！

## 🤝 贡献指南

欢迎提交Pull Request或Issue!

## 📜 开源协议

CC BY-NC-SA 4.0

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用开发框架
- [高德地图开放平台](https://lbs.amap.com/) - 地图服务
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架
- [Vue 3](https://vuejs.org/) - 前端框架

---

**智能旅行助手** - 让旅行计划变得简单而智能 🌈