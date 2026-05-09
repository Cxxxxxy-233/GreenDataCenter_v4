# 数据中心绿电一体化方案智能规划系统

## 项目启动指南

本文档提供项目启动的完整步骤，适用于新成员加入或重新搭建开发环境。

---

## 目录

- [项目概述](#项目概述)
- [环境准备](#环境准备)
- [后端启动](#后端启动)
- [前端启动](#前端启动)
- [验证运行](#验证运行)
- [常见问题](#常见问题)

---

## 项目概述

本项目采用前后端分离架构：

| 组件 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| 前端 | Vue 3 + Vite + Element Plus | 5173/5174 | 用户界面 |
| 后端 | Python FastAPI + LangGraph | 8000 | API 服务与 AI 智能体 |

### 项目结构

```
GreenDataCenter_v4/
├── src/                          # 后端源代码
│   └── greendatacenter/
│       ├── server.py             # FastAPI 服务入口
│       ├── coordinator_v2.py      # AI 协调器
│       ├── graph/                # 智能体图结构
│       │   ├── build.py          # 图构建
│       │   ├── nodes.py          # 节点定义
│       │   └── state.py         # 状态管理
│       └── tools/                # 工具函数
│           ├── green_power_allocation.py  # 绿电分配
│           ├── cooling.py                # 制冷方案
│           └── power_supply_config.py    # 供电配置
├── frontend/                     # 前端源代码
│   ├── src/
│   │   ├── api/                  # API 封装
│   │   ├── views/                # 页面组件
│   │   └── App.vue               # 根组件
│   └── package.json
├── DEPENDENCIES.md               # 依赖说明
└── requirements.txt             # Python 依赖
```

---

## 环境准备

### 1. 安装 Python（>= 3.10）

推荐使用 [Anaconda](https://www.anaconda.com/) 或 [Python官网](https://www.python.org/) 安装。

验证安装：
```bash
python --version
# 应显示 Python 3.10.x 或更高版本
```

### 2. 安装 Node.js（>= 18.0）

推荐使用 [Node.js官网](https://nodejs.org/) LTS 版本安装。

验证安装：
```bash
node --version
# 应显示 v18.x.x 或更高版本
npm --version
# 应显示 9.x.x 或更高版本
```

### 3. 克隆项目

```bash
git clone <repository_url>
cd GreenDataCenter_v4
```

### 4. 安装后端依赖

```bash
# 使用 pip 安装（推荐）
pip install -r requirements.txt

# 或使用 pyproject.toml 安装
pip install -e .
```

### 5. 安装前端依赖

```bash
cd frontend
npm install
```

### 6. 配置环境变量

```bash
# 在项目根目录创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入你的 LLM API Key
notepad .env  # Windows
# 或
nano .env     # Linux/Mac
```

`.env` 文件内容：
```bash
LLM_API_KEY=your_api_key_here
```

### 7. 创建必要目录

```bash
# Windows PowerShell
New-Item -ItemType Directory -Path "src/greendatacenter/tools/csv" -Force
New-Item -ItemType Directory -Path "src/greendatacenter/output" -Force

# Linux/Mac
mkdir -p src/greendatacenter/tools/csv
mkdir -p src/greendatacenter/output
```

---

## 后端启动

### 方式一：使用项目根目录命令启动（推荐）

```bash
# Windows PowerShell
$env:PYTHONPATH = "$PWD\src"
uvicorn src.greendatacenter.server:app --host 0.0.0.0 --port 8000

# Linux/Mac
export PYTHONPATH=$PWD/src
uvicorn src.greendatacenter.server:app --host 0.0.0.0 --port 8000
```

### 方式二：使用模块方式启动

```bash
# 设置 PYTHONPATH
$env:PYTHONPATH = "c:\完整路径\GreenDataCenter_v4\src"

# 进入后端目录
cd src/greendatacenter

# 启动服务
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```

### 方式三：使用 Python 直接运行

```bash
# 设置 PYTHONPATH 后直接运行
$env:PYTHONPATH = "$PWD\src"
python src/greendatacenter/server.py
```

### 后端启动成功标志

终端应显示：
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
[WARN] Failed to export workflow PNG: ...
AI系统协调器初始化完成
图节点: ['requirement_parser', 'draft_plan_agent', ...]
```

---

## 前端启动

### 开发模式启动

```bash
cd frontend
npm run dev
```

启动成功后，终端显示：
```
VITE v5.x.x  ready in xxx ms

  Local:   http://localhost:5173/
  # 如果 5173 被占用，会自动切换到 5174
  Local:   http://localhost:5174/
```

### 生产模式构建

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist` 目录。

### 预览生产构建

```bash
cd frontend
npm run preview
```

---

## 验证运行

### 1. 验证后端服务

在浏览器或终端访问：

```bash
curl http://localhost:8000/api/solutions
```

预期返回：
```json
{"solutions": [], "total": 0}
```

### 2. 验证前端服务

在浏览器访问：
```
http://localhost:5173
# 或
http://localhost:5174
```

### 3. 完整流程测试

1. 打开前端页面
2. 点击「配置参数」进入配置页面
3. 填写或加载示例参数
4. 点击「开始生成」
5. 观察方案生成页面的实时进度

---

## 常见问题

### Q1: 启动后端时报 `ModuleNotFoundError: No module named 'greendatacenter'`

**原因**：PYTHONPATH 未正确设置

**解决**：
```bash
# Windows PowerShell - 必须在项目根目录执行
$env:PYTHONPATH = "$PWD\src"

# Linux/Mac
export PYTHONPATH=$PWD/src
```

### Q2: 启动后端时报 `Permission denied` 错误

**原因**：缺少必要的目录权限

**解决**：
```bash
# 删除旧目录并重新创建
Remove-Item -Recurse -Force src/greendatacenter/tools/csv
Remove-Item -Recurse -Force src/greendatacenter/output

New-Item -ItemType Directory -Path "src/greendatacenter/tools/csv" -Force
New-Item -ItemType Directory -Path "src/greendatacenter/output" -Force
```

### Q3: 端口被占用

**原因**：8000 或 5173 端口已被其他程序占用

**解决**：

后端更换端口：
```bash
uvicorn src.greendatacenter.server:app --host 0.0.0.0 --port 8001
```
同时修改前端 `frontend/src/api/index.js` 中的 `BASE_URL`：
```javascript
const BASE_URL = 'http://localhost:8001'
```

前端会自动选择可用端口（5174 等），无需手动修改。

### Q4: LLM API 调用失败

**原因**：API Key 无效或余额不足

**解决**：
1. 检查 `.env` 文件中的 `LLM_API_KEY` 是否正确
2. 确认 API Key 有足够的调用额度
3. 检查网络是否能访问 LLM 服务

### Q5: 前端页面空白或显示错误

**原因**：后端未启动或连接失败

**解决**：
1. 确认后端服务已启动且运行在 8000 端口
2. 检查前端控制台网络请求是否显示 CORS 错误
3. 确认浏览器能访问 `http://localhost:8000`

### Q6: 方案生成卡在某个节点不动

**原因**：LLM 调用超时或工具执行时间过长

**解决**：
1. 等待几分钟观察是否继续
2. 检查后端终端是否有错误输出
3. 刷新页面重新开始

### Q7: pip 安装依赖失败

**原因**：网络问题或 Python 版本不兼容

**解决**：
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

---

## 快速命令汇总

```bash
# ===== 一键启动（PowerShell）=====

# 1. 克隆后进入目录
cd GreenDataCenter_v4

# 2. 安装依赖（如未安装）
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. 创建 .env 文件（如未创建）
# 编辑 .env 填入 LLM_API_KEY

# 4. 创建必要目录
New-Item -ItemType Directory -Path "src/greendatacenter/tools/csv" -Force
New-Item -ItemType Directory -Path "src/greendatacenter/output" -Force

# 5. 启动后端（终端1）
$env:PYTHONPATH = "$PWD\src"
uvicorn src.greendatacenter.server:app --host 0.0.0.0 --port 8000

# 6. 启动前端（终端2）
cd frontend
npm run dev
```

---

## 联系方式

如遇到本文档未覆盖的问题，请联系项目维护者。

---

## 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-05-09 | 1.0 | 初始版本 |
