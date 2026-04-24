# GreenDataCenter - 数据中心建设方案设计和推荐系统

## 项目简介

本项目是一个基于多专家协同决策架构的AI系统，用于数据中心建设方案的设计和推荐。系统通过经济性、供电可靠性和环保性三个领域的专家分析、交叉辩论、仲裁决策，生成兼顾多方需求的最优建设方案。

### 核心特性

- **多专家协作**: 经济性、可靠性、环保性三个领域专家独立分析
- **智能辩论**: 专家之间进行多轮讨论，达成共识
- **仲裁决策**: 综合各方意见，生成平衡的最优方案
- **流式输出**: 实时展示生成过程
- **鲁棒解析**: 多重JSON解析策略，提高系统稳定性

### 核心架构

```
用户输入 → 需求解析 → 顺序专家分析 → 专家辩论 → 仲裁决策 → 最终方案
                        ↓
            - 经济性分析专家
            - 供电可靠性专家
            - 环保性分析专家
```

## 技术栈

- **语言**: Python 3.10+
- **依赖管理**: uv
- **LLM框架**: LangChain
- **流程编排**: LangGraph
- **AI模型**: DeepSeek (https://api.deepseek.com)

## 快速开始

### 环境准备

#### 1. 安装依赖

```bash
# 使用uv安装依赖
uv sync
```

#### 2. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加你的DeepSeek API密钥
# LLM_API_KEY=sk-your-api-key-here
```

### 3. 生成示例输入

```bash
# 使用CLI生成示例
gdc example
```

### 4. 生成方案

```bash
# Python代码方式
uv run python -c "
import sys; sys.path.insert(0, 'src')
from greendatacenter import AISystemCoordinator

# 创建协调器
coordinator = AISystemCoordinator()

# 准备输入数据
input_data = {
    'name': '华东数据中心一期建设',
    'rack_count': 100,
    'total_power': 500,
    'tier_level': 3,
    'pue_target': 1.3,
    'green_power_ratio': 0.7,
    'budget': 2000
}

# 生成方案
result = coordinator.generate_solution(input_data=input_data)

# 检查结果
if result['success']:
    solution = result['solution']
    print(f'方案名称: {solution['name']}')
    print(f'综合评分: {solution['overall_scores']['overall']:.2f}')
"
```

### 5. 查看方案

生成的 `solution.json` 文件含完整的建设方案，包括：

- 方案名称和摘要
- 综合评分（经济性、可靠性、环保性）
- 关键指标（成本、PUE、绿电比例、可用性、碳排放）
- 各维度详细分析
- 权衡说明
- 风险评估
- 最终建议

## 项目结构

```
GreenDataCenter/
├── src/greendatacenter/        # 源代码
│   ├── __init__.py
│   ├── coordinator_v2.py         # AI系统协调器
│   ├── cli.py                    # CLI接口
│   ├── llm/                      # LLM配置
│   │   ├── __init__.py
│   │   └── config.py
│   ├── memory/                   # 记忆模块
│   │   ├── __init__.py
│   │   └── memory_manager.py     # 专家共享记忆
│   └── graph/                    # LangGraph相关
│       ├── __init__.py
│       ├── state.py               # 图状态定义
│       ├── nodes.py               # 所有节点函数
│       ├── edges.py               # 边和条件函数
│       └── build.py               # 图构建器
├── tests/                       # 测试代码
├── docs/                         # 文档
│   ├── design/                  # 设计文档
│   │   └── backend_ai_system.md  # 后端AI系统详细架构
│   ├── user/                    # 用户文档
│   │   ├── user_guide.md         # 用户手册
│   │   └── quick-start.md      # 快速开始指南
│   ├── api/                     # API文档
│   ├── development/              # 开发文档
│   ├── domain/                  # 领域知识
│   │   ├── tier-standards.md    # Tier标准
│   │   ├── pue-standards.md     # PUE标准
│   │   ├── power-standards.md   # 电力规范
│   │   └── cooling-standards.md # 制冷规范
│   ├── deployment/              # 部署文档
│   ├── requirements/           # 需求文档
│   └── architecture.md        # 架构文档
├── data/                        # 数据文件
├── pyproject.toml               # 项目配置
└── .env.example                 # 环境变量模板
```

## 使用示例

### 基本使用

```python
from greendatacenter import AISystemCoordinator

# 创建协调器
coordinator = AISystemCoordinator()

# 准备输入数据
input_data = {
    "name": "华东数据中心一期建设",
    "rack_count": 100,
    "total_power": 500,
    "tier_level": 3,
    "pue_target": 1.3,
    "green_power_ratio": 0.7,
    "budget": 2000
}

# 生成方案
result = coordinator.generate_solution(input_data=input_data)

# 检查结果
if result["success"]:
    solution = result["solution"]
    print(f"方案名称: {solution['name']}")
    print(f"综合评分: {solution['overall_scores']['overall']:.2f}")
```

### 高级使用

```python
# 获取系统状态
status = coordinator.get_system_status()
print(f"版本: {status['coordinator']['version']}")
print(f"节点: {status['graph']['nodes']}")

# 解释方案
explanation = coordinator.explain_solution(
    solution=result["solution"],
    detail_level="full"
)
print(explanation)

# 清空记忆
coordinator.clear_memory()
```

### CLI命令

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

## 输入参数说明

| 参数 | 类型 | 必填 | 说明 |
|----------|------|----------|------|
| name | string | 是 | 项目名称 |
| rack_count | integer | 否 | 机柜数量 |
| total_power | float | 是 | 总功率需求（kW） |
| tier_level | integer | 否 | 可靠性等级（1-4） |
| pue_target | float | 否 | PUE目标值 |
| floor_area | float | 否 | 建筑面积（m²） |
| green_power_ratio | float | 否 | 绿电比例（0-1） |
| budget | float | 否 | 预算上限（万元） |
| power_density | float | 否 | 功率密度（kW/机柜） |
| bandwidth | float | 否 | 带宽需求（Gbps） |
| objectives | array | 否 | 项目目标列表 |
| constraints | array | 否 | 约束条件列表 |
| priorities | object | 否 | 优先级设置（经济性/可靠性/环保性） |

## 输出结果说明

### JSON输出格式

```json
{
  "name": "方案名称",
  "summary": "方案摘要",
  "overall_scores": {
    "economic": 0.85,
    "reliability": 0.9,
    "environmental": 0.88,
    "overall": 0.88
  },
  "key_metrics": {
    "total_cost": 1800.0,
    "pue": 1.3,
    "green_power_ratio": 0.7,
    "tier_level": 3,
    "expected_availability": 99.98,
    "annual_carbon_emission": 250.0
  },
  "economic_section": {...},
  "power_reliability_section": {...},
  "environmental_section": {...},
  "trade_offs": [...],
  "risks": [...],
  "recommendations": [...],
  "confidence": 0.85
}
```

## 性能指标

- **平均生成时间**: ~110秒
- **成功率**: >95%
- **共识达成**: 通常1轮（共识度0.8-0.97）
- **API调用**: 每个方案约4-7次

## 文档索引

### 快速入门

- [用户指南](docs/user_guide.md) - 快速开始使用系统
- [快速开始指南](docs/user/quick-start.md) - 详细的启动和测试步骤

### 技术文档

- [后端AI系统架构](docs/design/backend_ai_system.md) - 完整的技术架构文档
- [领域知识](docs/domain/README.md) - 领域标准和规范

### 开发文档

- [开发文档](docs/development/README.md) - 开发规范和指南

### 部署文档

- [部署文档](docs/deployment/README.md) - 部署指南和最佳实践

### 工作总结

- [工作总结](docs/work-summary.md) - 本次文档工作的详细总结

## 设计决策

### 为什么使用LangGraph？

- 明确的流程编排，清晰的状态转换
- 可观察的执行过程，可见的节点和边路径
- 易于扩展新的节点和边
- 内置条件路由和循环支持

### 为什么顺序执行专家分析？

- **原始设计**: 并行执行以提高效率
- **实际实现**: 顺序执行（经济性→可靠性→环保性）
- **原因**: 多个LLM同时执行时的流式输出干扰导致JSON解析错误
- **权衡**: 执行时间略长（约2分钟），但解析可靠性大幅提高

### 为什么使用共享记忆？

- 专家需要了解其他专家的观点
- 辩论轮次需要记录对话历史
- 仲裁决策需要完整上下文

### 为什么需要不同温度？

- 经济性: 0.5 - 平衡创新和稳定性
- 供电可靠性: 0.3 - 追求准确和确定性
- 环保性: 0.4 - 平衡分析和创造性

## 扩展性

### 添加新专家

1. 创建新节点类在 `graph/nodes.py`
2. 添加状态字段在 `graph/state.py`
3. 添加节点在图构建中 `graph/build.py`
4. 添加对应的LLM创建函数在 `llm/config.py`

### 修改辩论规则

编辑 `DebateRoundNode` 在 `graph/nodes.py`:
- 改变发言顺序
- 修改共识评估逻辑
- 更新收敛条件

### 修改仲裁策略

编辑 `ArbitratorNode` 在 `graph/nodes.py`:
- 调整权重计算
- 修改输出格式
- 添加新的权衡逻辑

## 故障排查

### 常见问题

1. **ModuleNotFoundError**
   - 运行 `uv sync` 安装依赖
   - 检查虚拟环境是否激活

2. **ImportError**
   - 检查相对导入路径是否正确
   - 检查模块是否在正确位置

3. **API连接错误**
   - 检查 `LLM_API_KEY` 是否正确设置
   - 验证API密钥是否有效
   - 检查网络连接是否正常

4. **JSON解析错误**
   - 系统会自动使用默认值继续
   - 查看日志中的警告信息

5. **LangGraph执行错误**
   - 检查状态对象结构是否匹配
   - 确保节点函数返回正确的状态更新

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
