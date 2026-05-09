# 项目依赖文档

本文档整理了数据中心绿电一体化方案智能规划系统的所有依赖，便于多人协作时快速搭建开发环境。

---

## 环境要求

| 类别 | 要求 |
|------|------|
| Python | >= 3.10 |
| Node.js | >= 18.0 |
| npm | >= 9.0 |

---

## 后端依赖 (Python)

### 核心依赖

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| pydantic | >= 2.0.0 | 数据模型验证 |
| pydantic-settings | >= 2.0.0 | Pydantic 配置管理 |
| loguru | >= 0.7.0 | 日志记录 |
| rich | >= 13.0.0 | 终端富文本输出 |
| typing-extensions | >= 4.5.0 | 类型提示扩展 |
| typer | >= 0.24.1 | CLI 框架 |

### AI/LLM 相关

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| langchain-core | >= 1.2.25 | LangChain 核心 |
| langchain | >= 1.2.15 | LangChain 主库 |
| langchain-openai | >= 1.1.14 | OpenAI 集成 |
| langchain-community | >= 0.2.16 | LangChain 社区组件 |
| langgraph | >= 1.1.8 | 多智能体图编排 |

### 数据处理与科学计算

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| numpy | >= 1.26.0 | 数值计算 |
| pandas | >= 2.2.0 | 数据分析 |
| scipy | >= 1.12.0 | 科学计算 |
| matplotlib | >= 3.8.0 | 数据可视化 |

### 太阳能/风能仿真

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| pvlib | >= 0.10.5 | 光伏系统仿真 |

### Web 服务

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| fastapi | >= 0.104.0 | Web 框架 |
| uvicorn | >= 0.24.0 | ASGI 服务器 |
| python-dotenv | >= 1.2.2 | 环境变量加载 |

### 其他工具

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| requests | >= 2.32.0 | HTTP 请求 |
| geopy | >= 2.4.1 | 地理编码 |

### 可选依赖

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| openai | >= 1.0.0 | OpenAI API 客户端 |
| anthropic | >= 0.18.0 | Anthropic API 客户端 |

### 开发依赖

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| pytest | >= 7.4.0 | 单元测试 |
| pytest-asyncio | >= 0.21.0 | 异步测试支持 |
| pytest-cov | >= 4.1.0 | 测试覆盖率 |
| black | >= 23.0.0 | 代码格式化 |
| ruff | >= 0.1.0 | 代码检查 |
| mypy | >= 1.5.0 | 类型检查 |

---

## 前端依赖 (Node.js)

### 核心依赖

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| vue | ^3.4.21 | Vue 3 框架 |
| vue-router | ^4.3.0 | Vue 路由 |
| element-plus | ^2.6.1 | Element Plus UI 组件库 |
| @element-plus/icons-vue | ^2.3.2 | Element Plus 图标 |
| axios | ^1.6.7 | HTTP 客户端 |
| echarts | ^5.5.0 | ECharts 图表库 |

### 开发依赖

| 依赖包 | 版本要求 | 说明 |
|--------|----------|------|
| vite | ^5.4.21 | Vite 构建工具 |
| @vitejs/plugin-vue | ^5.0.4 | Vue 插件 |

---

## 环境变量配置

### 1. 后端环境变量 (.env)

在项目根目录创建 `.env` 文件：

```bash
LLM_API_KEY=your_api_key_here
```

### 2. 前端配置

前端 API 地址在 `frontend/src/api/index.js` 中配置：

```javascript
const BASE_URL = 'http://localhost:8000'
```

如需修改后端地址，修改此变量即可。

---

## 安装指南

### 1. 克隆项目

```bash
git clone <repository_url>
cd GreenDataCenter_v4
```

### 2. 后端安装

#### 使用 pip 安装

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装核心依赖
pip install -e .

# 安装所有可选依赖
pip install -e ".[dev,llm,web]"
```

#### 使用 pyproject.toml 安装

```bash
pip install -e .
```

### 3. 前端安装

```bash
cd frontend
npm install
```

### 4. 目录权限配置

确保以下目录存在且有写权限：

```bash
# 创建必要的目录
mkdir -p src/greendatacenter/tools/csv
mkdir -p src/greendatacenter/output

# 如果目录已存在但无写权限，修改权限
chmod 755 src/greendatacenter/tools/csv
chmod 755 src/greendatacenter/output
```

---

## 启动指南

### 1. 启动后端服务

```bash
# 设置 PYTHONPATH
export PYTHONPATH=$PWD/src  # Linux/Mac
# 或
$env:PYTHONPATH = "$PWD\src"  # Windows PowerShell

# 启动服务
cd src/greendatacenter
uvicorn server:app --host 0.0.0.0 --port 8000
```

或使用项目根目录启动：

```bash
cd GreenDataCenter_v4
$env:PYTHONPATH = "$PWD\src"
uvicorn src.greendatacenter.server:app --host 0.0.0.0 --port 8000
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

---

## 快速验证

### 后端健康检查

```bash
curl http://localhost:8000/api/solutions
```

### 查看后端日志

后端启动后会输出类似以下日志：

```
INFO:     Uvicorn running on http://0.0.0.0:8000
AI系统协调器初始化完成
图节点: ['requirement_parser', 'draft_plan_agent', ...]
```

---

## 常见问题

### 1. PYTHONPATH 设置问题

如果遇到 `ModuleNotFoundError: No module named 'greendatacenter'`，请确保正确设置 PYTHONPATH：

```bash
# Windows PowerShell
$env:PYTHONPATH = "c:\path\to\GreenDataCenter_v4\src"

# Linux/Mac
export PYTHONPATH=/path/to/GreenDataCenter_v4/src
```

### 2. 端口被占用

如果 8000 端口被占用，可以更换端口：

```bash
uvicorn src.greendatacenter.server:app --host 0.0.0.0 --port 8001
```

同时修改前端的 `BASE_URL`：

```javascript
const BASE_URL = 'http://localhost:8001'
```

### 3. 权限问题

如果遇到 `Permission denied` 错误，删除旧目录并重新创建：

```bash
rm -rf src/greendatacenter/tools/csv
rm -rf src/greendatacenter/output
mkdir -p src/greendatacenter/tools/csv
mkdir -p src/greendatacenter/output
```

### 4. LLM API Key 问题

如果 LLM 调用失败，检查 `.env` 文件中的 API Key 是否正确：

```bash
cat .env
```

确保格式为：`LLM_API_KEY=your_actual_key`

---

## 依赖更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-05-09 | 初始版本 |

