# API 文档

本目录包含GreenDataCenter系统的API接口说明。

## 概述

GreenDataCenter系统目前主要通过Python库（`AISystemCoordinator`）提供API，CLI接口通过此库实现。

## 核心API

### AISystemCoordinator

系统协调器，负责整体流程编排和状态管理。

#### `__init__()`

初始化AI系统协调器。

```python
coordinator = AISystemCoordinator()
```

**返回**: `AISystemCoordinator` 实例

**说明**:
- 创建共享记忆实例
- 构建LangGraph工作流
- 编译图以供执行

---

#### `generate_solution(input_data, on_stream_chunk=None)`

同步生成数据中心建设方案。

**参数**:
- `input_data` (dict): 用户输入数据
- `on_stream_chunk` (callable, optional): 流式输出回调函数

**返回**: `dict`
```python
{
    "success": bool,          # 是否成功生成
    "solution": dict,       # 生成的方案
    "streaming_output": list, # 流式输出记录
    "generation_time": float, # 生成耗时（秒）
    "error": str           # 错误信息（失败时）
}
```

**示例**:
```python
from greendatacenter import AISystemCoordinator

coordinator = AISystemCoordinator()

input_data = {
    "name": "华东数据中心一期建设",
    "rack_count": 100,
    "total_power": 500,
    "tier_level": 3,
    "pue_target": 1.3,
    "green_power_ratio": 0.7,
    "budget": 2000
}

result = coordinator.generate_solution(input_data=input_data)

if result["success"]:
    solution = result["solution"]
    print(f"方案名称: {solution['name']}")
    print(f"综合评分: {solution['overall_scores']['overall']}")
```

---

#### `generate_solution_async(input_data, on_stream_chunk=None)`

异步生成数据中心建设方案。

**参数**: 与 `generate_solution` 相同

**返回**: `dict` (异步，与同步版本结构相同)

---

#### `get_system_status()`

获取系统当前状态。

**返回**: `dict`
```python
{
    "coordinator": {
        "status": str,        # 状态 (ready/error)
        "version": str,       # 版本号
        "architecture": str, # 架构描述
        "last_activity": str  # 最后活动时间
    },
    "graph": {
        "nodes": list,        # 图节点列表
        "edges_count": int    # 边数量
    },
    "memory": {
        "type": str,           # 记忆类型
        "history_length": int,  # 历史记录长度
        "has_summary": bool    # 是否有摘要
    }
}
```

**示例**:
```python
status = coordinator.get_system_status()
print(f"版本: {status['coordinator']['version']}")
print(f"节点: {status['graph']['nodes']}")
```

---

#### `clear_memory()`

清空共享记忆。

**参数**: 无

**返回**: `None`

---

#### `explain_solution(solution, detail_level="summary")`

解释建设方案。

**参数**:
- `solution` (dict): 建设方案
- `detail_level` (str): 详细程度
  - `summary`: 摘要级别
  - `detail`: 详细级别
  - `full`: 完整级别

**返回**: `str` - 解释文本

---

## 数据模型

### GraphState

LangGraph图状态定义。

**字段**:
```python
{
    # 输入
    "requirement": dict,        # 用户需求
    "user_id": str,            # 用户ID

    # 流程控制
    "current_step": str,       # 当前步骤
    "next_step": str,           # 下一步骤

    # 辩论控制
    "debate_round": int,        # 当前辩论轮次
    "max_debate_rounds": int,  # 最大辩论轮次
    "consensus_reached": bool, # 是否达成共识
    "should_continue_debate": bool,  # 是否继续辩论

    # 专家意见
    "economic_opinion": ExpertOpinion,
    "power_reliability_opinion": ExpertOpinion,
    "environmental_opinion": ExpertOpinion,

    # 辩论历史
    "debate_history": list,

    # 评估
    "consensus_score": float, # 共识评分

    # 输出
    "solution": dict,          # 最终方案
    "streaming_output": list    # 流式输出
}
```

### ExpertOpinion

专家意见数据模型。

**字段**:
```python
{
    "expert_type": str,        # 专家类型
    "expert_name": str,        # 专家名称
    "summary": str,            # 意见摘要
    "reasoning": str,           # 推理过程
    "scores": dict,            # 评分
    "metrics": dict,            # 关键指标
    "recommendations": list,    # 建议
    "concerns": list,          # 关切点
    "confidence": float          # 置信度
}
```

### DebateMessage

辩论消息数据模型。

**字段**:
```python
{
    "speaker": str,             # 发言者
    "listener": str,           # 倾听者
    "message": str,            # 消息内容
    "message_type": str,        # 消息类型 (statement/response)
}
```

## 使用示例

### 基本使用

```python
from greendatacenter import AISystemCoordinator

# 创建协调器
coordinator = AISystemCoordinator()

# 准备输入
input_data = {
    "name": "测试数据中心",
    "rack_count": 50,
    "total_power": 250
}

# 生成方案
result = coordinator.generate_solution(input_data=input_data)

if result["success"]:
    solution = result["solution"]
    # 处理方案
    print(f"方案: {solution['name']}")
    print(f"评分: {solution['overall_scores']['overall']}")
```

### 流式输出

```python
def on_stream_chunk(chunk: str):
    """处理流式输出"""
    print(chunk, end="", flush=True)

result = coordinator.generate_solution(
    input_data=input_data,
    on_stream_chunk=on_stream_chunk
)
```

### 异步使用

```python
import asyncio

async def generate_solution_async():
    coordinator = AISystemCoordinator()
    input_data = {...}
    result = await coordinator.generate_solution_async(
        input_data=input_data
    )
    return result

# 运行
result = asyncio.run(generate_solution_async())
```

### 获取系统状态

```python
status = coordinator.get_system_status()
print(f"版本: {status['coordinator']['version']}")
print(f"图节点: {status['graph']['nodes']}")
```

### 解释方案

```python
explanation = coordinator.explain_solution(
    solution=result["solution"],
    detail_level="full"  # summary/detail/full
)
print(explanation)
```

## 错误处理

### 常见错误

#### 1. ModuleNotFoundError

**原因**: 模块未找到

**解决方法**:
```bash
uv sync
```

#### 2. ImportError

**原因**: 导入错误

**解决方法**:
- 检查模块路径
- 确保虚拟环境已激活
- 检查依赖是否安装

#### 3. API连接错误

**原因**: API密钥无效或网络问题

**解决方法**:
```bash
# 检查API密钥
uv run python tests/test_api.py

# 验证网络连接
ping api.deepseek.com
```

#### 4. JSON解析错误

**原因**: LLM输出格式错误

**处理方式**: 系统会自动使用默认值继续

#### 5. LangGraph执行错误

**原因**: 状态结构不匹配

**解决方法**:
- 检查节点函数返回值
- 确保状态字段正确

## CLI接口

系统通过 `gdc` 命令行工具提供CLI接口。记得前面加上uv run

### 命令

#### `gdc generate input_file -o output_file --detail level`

生成数据中心建设方案。

**参数**:
- `input_file`: 输入JSON文件路径
- `-o, --output-file`: 输出文件路径（可选）
- `-d, --detail`: 详细级别 (summary/detail/full)

#### `gdc status`

显示系统状态。

#### `gdc example`

生成示例输入文件。

#### `gdc explain solution_file --detail level`

解释建设方案。

### CLI使用示例

```bash
# 生成方案
gdc generate input.json -o solution.json --detail full

# 查看状态
gdc status

# 生成示例
gdc example

# 解释方案
gdc explain solution.json --detail full
```

## 性能考虑

- **生成时间**: 正常情况下约100-180秒
- **API调用**: 每个方案约4-7次API调用
- **内存占用**: 较低（流式处理）
- **并发能力**: 支持异步并发生成

## 未来API规划

### REST API (计划中)

未来版本将提供RESTful API接口：

- POST `/api/v1/solutions/generate` - 生成方案
- GET `/api/v1/solutions/{id}` - 获取方案
- GET `/api/v1/status` - 获取系统状态
- POST `/api/v1/solutions/{id}/explain` - 解释方案

### WebSocket API (计划中)

支持实时流式输出的WebSocket接口。

## 扩展性

### 添加新节点

1. 在 `graph/nodes.py` 创建新节点类
2. 在 `graph/state.py` 添加必要的状态字段
3. 在 `graph/build.py` 添加节点到图
4. 更新文档

### 添加新专家

1. 在 `graph/nodes.py` 创建新的专家节点类
2. 在 `llm/config.py` 添加对应的LLM创建函数
3. 更新 GraphState 以包含新专家的意见
4. 更新文档

### 添加CLI命令

1. 在 `cli.py` 添加新命令
2. 使用typer装饰器定义参数
3. 实现命令逻辑
4. 更新文档
