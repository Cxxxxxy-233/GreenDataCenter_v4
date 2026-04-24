# 后端 AI 系统架构 (v2.0 - LangGraph 版本)

## 系统概述

基于 LangChain 和 LangGraph 的数据中心建设方案设计与推荐系统。

### 核心架构

```
用户输入
  -> 需求解析器节点
  -> 多专家顺序分析
  -> 辩论循环（最多5轮）
  -> 仲裁者节点
  -> 输出节点
           ↓
    - 经济分析专家
    - 供电可靠性专家
    - 环境分析专家
```

## 技术栈

- **语言**: Python 3.10+
- **依赖管理**: uv
- **大语言模型(LLM)框架**: LangChain
- **流程编排**: LangGraph
- **模型**: DeepSeek (https://api.deepseek.com/v1, 模型: deepseek-chat)

## 目录结构

```
src/greendatacenter/
├── __init__.py              # 主入口
├── coordinator_v2.py         # AI 系统协调器
├── cli.py                   # 命令行界面
├── llm/                      # LLM 配置
│   ├── __init__.py
│   └── config.py             # LLM 实例
├── memory/                    # 记忆模块
│   ├── __init__.py
│   └── memory_manager.py     # 专家共享记忆
├── graph/                     # LangGraph 相关
│   ├── __init__.py
│   ├── state.py              # 图状态定义
│   ├── nodes.py              # 所有节点函数
│   ├── edges.py              # 边与条件函数
│   └── build.py              # 图构建器
└── models/                    # 数据模型（旧版本，未使用）
```

## 核心组件

### 1. LLM 配置 (llm/config.py)

- **get_llm()**: 支持流式输出的通用 LLM 创建器
  - 基础 URL: https://api.deepseek.com
  - 模型: deepseek-chat
- **create_economic_llm()**: 经济专家 LLM (温度参数=0.5, 最大 token=1500)
- **create_power_reliability_llm()**: 供电可靠性专家 LLM (温度参数=0.3, 最大 token=1500)
- **create_environmental_llm()**: 环境专家 LLM (温度参数=0.4, 最大 token=1500)
- **create_arbitrator_llm()**: 仲裁者 LLM (温度参数=0.5, 最大 token=2500)
- **create_requirement_parser_llm()**: 需求解析器 LLM (温度参数=0.3, 最大 token=1000)

所有 LLM 均支持带有回调处理程序的流式输出，以实现实时监控。

### 2. 记忆管理 (memory/memory_manager.py)

- **ExpertSharedMemory**: 专家共享记忆类
  - 存储专家意见以实现上下文感知
  - 存储辩论对话历史
  - 在分析期间为 LLM 提供记忆上下文
  - 提供 clear 方法用于在每次运行之间重置

### 3. 图状态 (graph/state.py)

- **GraphState**: LangGraph 状态定义
  - 输入: requirement (需求), user_id (用户ID)
  - 流程控制: current_step (当前步骤), next_step (下一步)
  - 辩论控制: debate_round (辩论轮次), max_debate_rounds (最大辩论轮次), consensus_reached (是否达成共识), should_continue_debate (是否应继续辩论)
  - 专家意见: economic_opinion (经济意见), power_reliability_opinion (供电可靠性意见), environmental_opinion (环境意见)
  - 辩论历史: debate_history
  - 评估: consensus_score (共识得分)
  - 输出: solution (方案), streaming_output (流式输出)

### 4. 图节点 (graph/nodes.py)

#### RequirementParserNode (需求解析器节点)
- 功能: 解析用户输入
- 输入: 原始需求数据
- 输出: 结构化需求对象
- 特性:
  - 补充缺失参数
  - 根据行业标准设置合理的默认值
  - 输出格式: 包含所有必填字段的 JSON

#### EconomicAnalysisNode (经济分析节点)
- 功能: 经济分析专家
- 评分维度:
  - cost_efficiency (成本效益，0-1)
  - roi (投资回报率，0-1)
- 关键指标:
  - total_cost (总成本，万元)
  - cost_per_rack (单机柜成本)
  - roi (投资回报率，0-1)
  - payback_period (投资回收期，年)
- 温度参数: 0.5 (平衡创新与稳定性)
- JSON 解析: 具有多种回退策略，鲁棒性强

#### PowerReliabilityAnalysisNode (供电可靠性分析节点)
- 功能: 供电可靠性分析专家
- 评分维度:
  - reliability (可靠性，0-1)
  - availability (可用性，0-1)
- 关键指标:
  - tier_level (Tier 等级，1-4)
  - expected_availability (预期可用性，%)
  - annual_downtime (年宕机时间，小时)
  - ups_configuration (UPS 配置)
  - ups_capacity (UPS 容量，kVA)
  - distribution_reliability (配电可靠性，0-1)
- 温度参数: 0.3 (追求准确性与确定性)
- JSON 解析: 具有多种回退策略，鲁棒性强

#### EnvironmentalAnalysisNode (环境分析节点)
- 功能: 环境分析专家
- 评分维度:
  - environmental_score (环境得分，0-1)
  - pue_score (PUE 得分，0-1)
  - green_power_score (绿电得分，0-1)
  - carbon_efficiency (碳效率，0-1)
- 关键指标:
  - pue_target (PUE 目标)
  - green_power_ratio (绿电比例，0-1)
  - annual_carbon_emission (年碳排放量，吨)
  - carbon_per_rack (单机柜碳排放)
- 温度参数: 0.4 (平衡分析与创造力)
- JSON 解析: 具有多种回退策略，鲁棒性强

#### DebateRoundNode (辩论轮次节点)
- 功能: 组织一轮专家辩论
- 辩论机制:
  - 专家轮流发言（经济 -> 供电 -> 环境）
  - 每轮包含3次陈述
  - 基于专家评分方差评估共识
- 收敛条件:
  - 共识度 >= 0.8: 提前停止
  - 最多5轮: 强制停止
  - should_continue (是否继续) 标志: 动态控制
- 共识计算: 1 - 专家评分的标准差

#### ArbitratorNode (仲裁者节点)
- 功能: 综合最终方案
- 决策依据:
  - 专家意见一致性
  - 冲突分析
  - 生成权衡方案
- 输出结构:
  ```json
  {
    "name": "方案名称",
    "summary": "方案摘要",
    "overall_scores": {...},
    "key_metrics": {...},
    "economic_section": {...},
    "power_reliability_section": {...},
    "environmental_section": {...},
    "trade_offs": [...],
    "risks": [...],
    "recommendations": [...],
    "confidence": 0.85
  }
  ```
- 温度参数: 0.5 (平衡所有需求)
- JSON 解析: 具有多种回退策略，鲁棒性强

#### OutputNode (输出节点)
- 功能: 输出最终方案
- 标记工作流完成
- 显示关键方案指标

### 5. 边函数 (graph/edges.py)

- **should_continue_debate()**: 判断辩论是否应继续
  - 检查: consensus_reached (是否达成共识)
  - 检查: max_rounds_reached (是否达到最大轮次)
  - 检查: should_continue_debate (是否应继续辩论) 标志
- 返回: "continue" (继续) 或 "stop" (停止)

- **check_debate_status()**: 根据辩论状态进行路由
- 返回: "continue" (继续) 或 "end" (结束)

### 6. 图构建器 (graph/build.py)

- **build_data_center_graph()**: 构建主工作流图
  总共 7 个节点
  - 入口点: requirement_parser (需求解析器)
  - 顺序执行: 经济 -> 供电 -> 环境（为避免输出干扰）
  - 条件循环: 辩论轮次
  - 顺序执行: 仲裁者，输出

## 用法

### 命令行指令

```bash
# 设置 API 密钥 
# 编辑 .env 并添加您的 DeepSeek API 密钥

# 生成示例输入
uv run gdc example

# 生成方案
uv run gdc generate example_input.json -o solution.json --detail full

# 检查系统状态
uv run gdc status

# 解释方案
uv run gdc explain solution.json
```

### Python 代码用法

```python
from greendatacenter import AISystemCoordinator

# 创建协调器
coordinator = AISystemCoordinator()

# 准备输入数据
input_data = {
    "name": "华东数据中心一期",
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
    streaming_output = result["streaming_output"]
    print(f"方案: {solution.get('name')}")
    print(f"总分: {solution.get('overall_scores', {}).get('overall', 0):.2f}")
```

## 输入格式

### JSON 输入示例

```json
{
  "name": "华东数据中心一期",
  "rack_count": 100,
  "total_power": 500,
  "power_density": 5,
  "tier_level": 3,
  "pue_target": 1.3,
  "floor_area": 500,
  "green_power_ratio": 0.7,
  "budget": 2000,
  "bandwidth": 1000,
  "objectives": ["降低 PUE", "提高可靠性", "控制成本"],
  "constraints": ["预算 2000 万元", "场地 500m²"],
  "priorities": {
    "economic": 3,
    "reliability": 5,
    "environmental": 4
  }
}
```

### 输入参数

| 参数 | 类型 | 必填 | 描述 |
|----------|------|----------|------|
| name | str | 是 | 需求名称 |
| rack_count | int | 否 | 机柜数量（数值） |
| total_power | float | 是 | 总功率需求 (kW) |
| tier_level | int | 否 | 可靠性等级 (1-4) |
| pue_target | float | 否 | PUE 目标值 |
| green_power_ratio | float | 否 | 绿电比例 (0-1) |
| budget | float | 否 | 预算上限（万元） |
| power_density | float | 否 | 功率密度 (kW/机柜) |
| floor_area | float | 否 | 占地面积 (m²) |
| bandwidth | float | 否 | 带宽需求 (Gbps) |
| priorities | dict | 否 | 优先级设置 (经济/可靠性/环境) |

## 输出格式

### JSON 输出示例

```json
{
  "name": "华东数据中心一期建设方案 v1.0",
  "summary": "基于 100 个机柜、500kW 功率需求，满足 Tier 3 标准，PUE 目标 1.3，绿电比例 70%，总分 0.88。",
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
    "annual_carbon_emission": 250.0,
    "roi": 0.12
  },
  "economic_section": {
    "description": "经济方案描述",
    "content": {"total_cost": 1800, "roi": 0.12},
    "recommendations": ["建议 1"]
  },
  "power_reliability_section": {
    "description": "供电可靠性方案描述",
    "content": {"tier_level": 3, "ups_configuration": "2N UPS"},
    "recommendations": ["建议 1"]
  },
  "environmental_section": {
    "description": "环境方案描述",
    "content": {"pue": 1.3, "green_power_ratio": 0.7},
    "recommendations": ["建议 1"]
  },
  "trade_offs": [
    {"conflict": "成本 vs 可靠性", "resolution": "通过优化优先保证可靠性"}
  ],
  "risks": [
    {"type": "供电", "description": "风险描述"}
  ],
  "recommendations": [
    "最终建议 1",
    "最终建议 2"
  ],
  "confidence": 0.85,
  "generation_time": 45.2,
  "created_at": "2024-04-19T10:30:50"
}
```

## 环境变量

创建 `.env` 文件:

```env
# 用于 LLM 的 DeepSeek API 密钥
LLM_API_KEY=your_deepseek_api_key_here

# 可选：用于搜索的 Tavily API 密钥
TAVILY_API_KEY=your_tavily_api_key_here
```

## 设计决策

### 1. 为什么使用 LangGraph？

- 具有清晰状态转换的显式流程编排
- 通过可见的节点和边路径实现执行的可观察性
- 易于扩展新的节点和边
- 内置支持条件路由和循环

### 2. 为什么使用共享记忆？

- 专家需要了解其他专家的观点
- 辩论轮次需要记录对话历史
- 仲裁者需要完整的上下文

### 3. 为什么为不同专家设置不同的温度参数？

- 经济：0.5 - 平衡创新与稳定性
- 供电可靠性：0.3 - 追求准确性与确定性
- 环境：0.4 - 平衡分析与创造力

### 4. 为什么采用顺序专家分析而不是并行？

- **初始设计**: 并行执行以提高效率
- **实际实现**: 顺序执行（经济 -> 供电 -> 环境）
- **原因**: 当多个 LLM 同时执行时，流式输出相互干扰，导致 JSON 解析错误和输出混乱
- **权衡**: 以稍长的执行时间（约 2 分钟）换取可靠得多的解析

### 5. 为什么设置这些辩论收敛标准？

- 共识度 >= 0.8: 避免无休止的辩论
- 最多 5 轮: 限制计算成本
- should_continue (是否继续) 标志: 动态流程控制

### 6. 为什么需要鲁棒的 JSON 解析？

- LLM 的输出可能会被包装在 markdown 代码块中
- JSON 结构可能是嵌套的
- 流式传输有时会导致格式问题
- 多种回退策略可确保系统可靠性

## 示例输出

这是由系统生成的真实示例：

```json
{
  "name": "高效可靠绿色数据中心综合解决方案",
  "summary": "本方案在平衡经济性、可靠性与环保性的基础上，通过优化能效设计、提升绿色电力比例、增强供电稳定性，实现ROI提升至12%、可用性99.98%、年碳排放降至1500吨的综合目标。",
  "overall_scores": {
    "economic": 0.78,
    "reliability": 0.92,
    "environmental": 0.85,
    "overall": 0.85
  },
  "key_metrics": {
    "total_cost": 18500000,
    "pue": 1.25,
    "green_power_ratio": 0.7,
    "tier_level": 3,
    "expected_availability": 99.98,
    "annual_carbon_emission": 1500
  },
  "economic_section": {
    "description": "优化初始投资结构，通过高效PUE设计降低运营成本，同时拓展增值服务提升收入，使ROI从11.1%提升至12%",
    "content": {
      "total_cost": 18500000,
      "roi": 0.12
    },
    "recommendations": [
      "采用间接蒸发冷却+液冷混合制冷方案，将PUE从1.3优化至1.25，预计降低年电力成本15%",
      "增加云服务与边缘计算增值服务模块，目标年收入提升至600万元"
    ]
  },
  "power_reliability_section": {
    "description": "维持Tier III标准2N UPS架构，增加储能系统缓冲绿色能源波动，配置柴油发电机保障长时间供电，可用性达99.98%",
    "content": {
      "tier_level": 3,
      "ups_configuration": "2N+储能系统"
    },
    "recommendations": [
      "增加500kWh储能电池系统，平滑绿色能源波动，保障UPS输入稳定性",
      "配置800kW柴油发电机作为二级备用，确保72小时持续供电能力"
    ]
  },
  "environmental_section": {
    "description": "通过提升绿色电力比例至70%、采用低GWP制冷剂、实施余热回收，将年碳排放从1872吨降至1500吨",
    "content": {
      "pue": 1.25,
      "green_power_ratio": 0.7
    },
    "recommendations": [
      "绿色电力比例从60%提升至70%，通过采购绿证与建设分布式光伏实现",
      "制冷剂从R134a更换为R1234ze(GWP<1)，降低制冷剂泄漏碳排放",
      "实施液冷系统余热回收，为办公区提供冬季供暖"
    ]
  },
  "trade_offs": [
    {
      "conflict": "经济性vs环保性",
      "resolution": "接受初始投资增加5%（约50万元）用于绿色电力与高效制冷系统，通过降低运营成本在3年内收回增量投资"
    }
  ],
  "risks": [
    {
      "type": "运营成本风险",
      "description": "电力价格波动可能影响PUE优化带来的成本节约效果，需签订长期购电协议锁定部分电价"
    }
  ],
  "recommendations": [
    "分阶段实施：第一期完成基础2N供电与高效制冷系统，第二期增加储能与光伏系统",
    "建立综合监控平台，集成电力、能效、碳排放在线监测与预警功能"
  ],
  "confidence": 0.88,
  "generation_time": 109.67
}
```

## 性能指标

- **平均生成时间**: 约 110 秒
- **成功率**: >95% (得益于鲁棒的 JSON 解析)
- **共识达成情况**: 通常只需 1 轮 (共识得分为 0.8-0.97)
- **内存使用**: 中等 (用于存储对话历史)
- **API 调用**: 每次方案生成 4-7 次 (取决于辩论轮次)

## 可扩展性

### 添加新专家代理

1. 在 `graph/nodes.py` 中创建新的节点类
2. 在 `graph/state.py` 中添加状态字段
3. 在 `graph/build.py` 的图构建中添加节点
4. 在 `llm/config.py` 中添加相应的 LLM 创建器

### 修改辩论规则

编辑 `graph/nodes.py` 中的 `DebateRoundNode`:
- 更改发言顺序
- 修改共识评估逻辑
- 更新收敛条件

### 修改仲裁策略

编辑 `graph/nodes.py` 中的 `ArbitratorNode`:
- 调整权重计算
- 修改输出格式
- 添加新的权衡逻辑

## 故障排除

### 常见问题

1. **ModuleNotFoundError (模块未找到错误)**
   - 运行 `uv sync` 以安装依赖
   - 检查虚拟环境是否已激活

2. **ImportError (导入错误)**
   - 检查相对导入是否正确
   - 确保所有模块都在正确的位置

3. **LLM API Error (LLM API 错误)**
   - 检查 `.env` 文件中的 `LLM_API_KEY`
   - 验证 API 密钥对 DeepSeek 是否有效

4. **Encoding Issues (编码问题)**
   - 文件具有 UTF-8 编码声明
   - Windows 控制台可能会显示乱码 - 这是预期现象 (不影响功能)
   - JSON 输出会以正确的编码保存

5. **JSON Parse Error (JSON 解析错误)**
   - 检查 LLM 输出格式
   - 验证 JSON 结构是否与预期的 schema 匹配
   - 具有多种回退策略的鲁棒解析可以处理大多数问题

6. **LangGraph Execution Error (LangGraph 执行错误)**
   - 检查状态对象结构
   - 确保节点函数返回正确的状态更新
   - 验证图的边是否配置正确

## 未来增强功能

### 计划功能

1. **RAG 集成**: 增加检索增强生成，用于访问领域知识库
2. **多轮对话**: 启用追问和方案优化功能
3. **网络搜索集成**: 增加实时数据访问，以获取定价、法规等信息
4. **并行执行**: 配合适当的输出处理，重新启用并行专家分析
5. **性能优化**: 通过缓存和优化缩短生成时间
6. **方案对比**: 生成多个备选方案以供比较
7. **可视化输出**: 生成图表以更好地呈现方案

### 技术债务

1. **Unicode 字符处理**: 移除剩余导致编码问题的 Unicode 字符
2. **错误处理**: 改善错误提示和恢复机制
3. **测试**: 添加全面的单元测试和集成测试
4. **文档**: 添加详细的内联注释和 API 文档
5. **配置**: 将温度和其他参数设置为可配置项
