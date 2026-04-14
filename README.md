# intelligent-travel-planner
本项目是一个基于LangChain框架的智能旅行规划系统，能够根据用户输入的自然语言需求，自动生成个性化的旅行计划。系统结合了高德地图API和大语言模型（LLM），提供从景点推荐、天气查询到行程安排的一站式服务。

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
- **UI组件库**: Ant Design Vue
- **构建工具**: Vite
- **HTTP客户端**: Axios

## 📁 项目结构

```
Intelligent_travel_planning_vibe_coding/
├── AGENT.md              # 技术规范文档
├── README.md             # 项目介绍
├── requirements.txt      # Python依赖
├── backend/              # 后端代码
│   ├── app/              # 应用核心
│   │   ├── agents/       # Agent实现
│   │   ├── api/          # API路由
│   │   ├── config.py     # 配置管理
│   │   ├── services/     # 服务层
│   │   └── __init__.py   # 应用初始化
│   └── tests/            # 测试代码
└── frontend/             # 前端代码
    ├── src/              # 源代码
    └── index.html        # HTML模板
```

## ⚡ 快速启动

### 环境准备

1. **安装Python 3.8+** 和 **Node.js 16+**
2. **获取API密钥**:
   - 高德地图API Key: [申请地址](https://console.amap.com/)
   - LLM API Key: OpenAI/DeepSeek等提供商

### 配置环境变量

复制 `.env.example` 为 `.env` 并填入您的API密钥:

```bash
cp .env.example .env
```

编辑 `.env` 文件:

```ini
# ===================================
# LLM配置
# ===================================
LLM_MODEL_ID=qwen3.6-plus
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# ===================================
# 高德地图API配置
# ===================================
AMAP_API_KEY=your_amap_api_key_here
```

### 启动项目

#### 一键启动 (推荐)
```bash
python start.py
```

#### 手动启动
```bash
# 启动后端
cd backend && uvicorn app.api.main:app --host 0.0.0.0 --port 8000

# 启动前端
cd frontend && npm install && npm run dev
```

### 访问应用
打开浏览器访问: http://localhost:5173

## 🔒 安全说明

- **API密钥保护**: 所有敏感信息存储在 `.env` 文件中
- **版本控制安全**: `.env` 文件已添加到 `.gitignore`,不会提交到GitHub
- **前端安全**: 通过Vite环境变量机制安全暴露必要配置

## 🧪 测试

运行测试套件:
```bash
cd backend && python -m pytest tests/ -v
```

## 📄 文档

- **技术规范**: 查看 `AGENT.md` 了解详细架构设计
- **API文档**: 启动后端后访问 http://localhost:8000/docs

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📜 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

---

**智能旅行助手** - 让旅行计划变得简单而智能 🌈