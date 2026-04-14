# 智能旅行助手 - 技术规范文档

## 📋 文档概述
本文档详细描述了**智能旅行助手**项目的技术架构、实现细节和开发规范。本项目基于**LangChain框架**构建，采用现代化的前后端分离架构，实现了智能旅行规划的核心功能。

## 1. 项目概述

### 1.1 项目背景
智能旅行助手是一个AI驱动的旅行规划系统，旨在帮助用户快速生成个性化的旅行行程。系统能够理解自然语言输入（如"后天去北京玩三天"），自动解析时间、地点和天数，并结合真实景点数据生成详细的旅行计划。

### 1.2 核心价值
- **自然语言交互**: 用户可以用日常语言描述旅行需求
- **实时数据集成**: 集成高德地图API获取最新景点信息
- **智能行程规划**: 基于LLM的创造性决策能力生成个性化行程
- **多日行程优化**: 自动分配景点到不同日期，考虑地理位置和游览时间

### 1.3 系统特性
- 支持中文自然语言输入解析
- 实时获取高德地图景点数据
- 基于LangChain的智能Agent架构
- 响应式Web前端界面
- RESTful API设计

## 2. 系统架构模式

### 2.1 四层架构设计
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     API层       │───▶│    Agent层      │───▶│   Service层     │───▶│  外部服务层     │
│  (FastAPI)      │    │  (LangChain)    │    │ (API封装)       │    │ (高德+LLM)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 核心设计理念
- **职责分离**: 每层只负责特定职责，降低耦合度
- **LangChain集成**: 充分利用LangChain的链式调用和Agent能力
- **性能优化**: 单Agent执行模式替代理论上的多Agent方案
- **可扩展性**: 模块化设计便于功能扩展

## 3. 各层技术规范

### 3.1 API层 (FastAPI)
- **框架**: FastAPI 0.115.12
- **路由**: `/api/v1/trip-plan` POST接口
- **请求体**: JSON格式，包含`query`字段
- **响应体**: JSON格式，包含`trip_plan`字段
- **CORS**: 支持前端开发服务器跨域访问

### 3.2 Agent层 (LangChain)
- **框架**: LangChain Core 0.3.17 + LangChain OpenAI 0.2.8
- **架构**: 单Agent两阶段处理模式
  - **第一阶段**: 自然语言解析 → 结构化参数
  - **第二阶段**: 基于真实数据生成行程
- **Prompt模板**: 使用ChatPromptTemplate定义系统行为
- **输出解析**: StrOutputParser处理LLM响应

### 3.3 Service层
- **高德地图服务**: 封装高德地图REST API，提供景点搜索功能
- **LLM服务**: 封装LangChain OpenAI接口，提供统一的LLM调用
- **错误处理**: 统一的异常处理和重试机制

### 3.4 外部服务层
- **高德地图API**: 提供POI（兴趣点）搜索和地理编码服务
- **OpenAI API**: 提供GPT-4模型的自然语言处理能力
- **环境变量配置**: 所有API密钥通过环境变量管理

## 4. 前端架构规范

### 4.1 技术栈
- **框架**: Vue 3 + TypeScript
- **UI组件库**: Ant Design Vue
- **HTTP客户端**: Axios
- **构建工具**: Vite

### 4.2 前端分层结构
```
frontend/
├── src/
│   ├── api/          # API服务封装
│   ├── components/   # 可复用组件
│   ├── views/        # 页面视图
│   ├── App.vue       # 根组件
│   └── main.ts       # 应用入口
└── index.html        # HTML模板
```

### 4.3 API服务实现
- **基础URL**: `/api/v1` (开发环境代理到后端)
- **错误处理**: 统一的HTTP错误拦截和用户提示
- **加载状态**: 请求过程中的用户反馈

## 5. 完整请求处理流程

### 5.1 端到端数据流
```
用户输入 "后天去北京玩三天"
        ↓
前端发送 POST /api/v1/trip-plan {query: "后天去北京玩三天"}
        ↓
FastAPI接收请求，验证参数
        ↓
TripPlannerAgent.plan_trip() 调用
        ↓
第一阶段：解析自然语言 → {destination: "北京", start_date: "2026-04-16", days: 3}
        ↓
调用AmapService.get_attractions("北京")
        ↓
第二阶段：基于景点数据生成详细行程
        ↓
返回JSON响应包含完整旅行计划
        ↓
前端渲染行程结果
```

### 5.2 时间解析机制
- **相对时间处理**: "明天"、"后天"、"下周"等转换为具体日期
- **当前日期基准**: 基于系统当前时间（2026-04-14）
- **日期格式**: 统一使用YYYY-MM-DD格式

## 6. 协议使用规范

### 6.1 使用的协议
| 协议类型 | 用途 | 实现方式 |
|---------|------|----------|
| HTTP/HTTPS | API通信 | FastAPI内置支持 |
| JSON | 数据交换格式 | Pydantic模型序列化 |
| CORS | 跨域资源共享 | FastAPI CORSMiddleware |
| REST | API设计风格 | 标准RESTful接口 |

### 6.2 MCP协议弃用说明
项目最初考虑使用MCP（Model Context Protocol）进行Agent通信，但最终选择直接REST API调用，原因包括：
- **简化架构**: 避免额外的协议层复杂性
- **调试友好**: 直接API调用更容易调试和监控
- **性能优化**: 减少协议转换开销
- **稳定性**: REST API更加成熟稳定

## 7. 配置管理与部署

### 7.1 环境变量配置
```
# .env 文件示例
AMAP_API_KEY=your_amap_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

### 7.2 启动方式
- **一键启动**: `python run.py` (同时启动前后端)
- **手动启动后端**: `cd backend && uvicorn app.api.main:app --host 0.0.0.0 --port 8000`
- **手动启动前端**: `cd frontend && npm run dev`

### 7.3 目录结构
```
Intelligent_travel_planning_vibe_coding/
├── AGENT.md              # 本技术规范文档
├── README.md             # 项目介绍和使用指南
├── requirements.txt      # Python依赖
├── backend/              # 后端代码
│   ├── app/              # 应用核心代码
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

## 8. 数据模型与性能优化

### 8.1 Pydantic数据模型
```python
class TripPlanRequest(BaseModel):
    query: str = Field(..., description="用户的自然语言查询")

class TripPlanResponse(BaseModel):
    trip_plan: str = Field(..., description="生成的旅行计划")
```

### 8.2 TypeScript接口定义
```
interface TripPlanRequest {
  query: string;
}

interface TripPlanResponse {
  trip_plan: string;
}
```

### 8.3 性能优化策略
- **缓存机制**: 景点数据缓存减少API调用
- **异步处理**: 使用async/await提高并发性能
- **批量请求**: 合并多个LLM调用减少延迟
- **错误降级**: 网络失败时提供备用方案

## 9. 技术约束与最佳实践

### 9.1 系统要求
- **Python版本**: 3.8+
- **Node.js版本**: 16+
- **API依赖**: 高德地图API Key、OpenAI API Key

### 9.2 开发最佳实践
- **环境隔离**: 使用虚拟环境管理Python依赖
- **代码格式**: 遵循PEP 8和ESLint规范
- **测试覆盖**: 关键功能必须有单元测试
- **文档同步**: 代码变更时同步更新文档

### 9.3 已知问题与解决方案
- **LLM响应不稳定**: 实现重试机制和超时控制
- **API配额限制**: 添加请求频率限制和错误处理
- **中文编码问题**: 确保UTF-8编码一致性

---

**文档版本**: 1.0  
**最后更新**: 2026-04-14  
**技术栈**: LangChain + FastAPI + Vue 3