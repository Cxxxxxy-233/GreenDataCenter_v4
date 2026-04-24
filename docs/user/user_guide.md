# GreenDataCenter - 用户指南

## 快速开始

### 1. 安装依赖

```bash
# 使用uv安装依赖
uv sync
```

### 2. 配置API密钥

```bash
# 编辑.env文件，添加你的DeepSeek API密钥
# LLM_API_KEY=your_deepseek_api_key_here
```

### 3. 生成示例输入

```bash
# 生成示例输入文件
uv run python -c "import sys; sys.path.insert(0, 'src'); from greendatacenter.cli import app; app()" example
```

或者手动创建 `input.json`:

```json
{
  "name": "华东数据中心一期建设",
  "rack_count": 100,
  "total_power": 500,
  "power_density": 5,
  "tier_level": 3,
  "pue_target": 1.3,
  "floor_area": 500,
  "green_power_ratio": 0.7,
  "budget": 2000,
  "bandwidth": 1000,
  "objectives": ["降低PUE", "提高可靠性", "控制成本"],
  "constraints": ["预算2000万元", "场地500m²"],
  "priorities": {
    "economic": 3,
    "reliability": 5,
    "environmental": 4
  }
}
```

### 4. 生成解决方案

```bash
# Python代码方式
uv run python -c "
import sys; sys.path.insert(0, 'src')
from greendatacenter import AISystemCoordinator
import json

coordinator = AISystemCoordinator()
input_data = json.load(open('input.json', encoding='utf-8'))
result = coordinator.generate_solution(input_data=input_data)

if result['success']:
    with open('solution.json', 'w', encoding='utf-8') as f:
        json.dump(result['solution'], f, indent=2, ensure_ascii=False)
    print('方案已保存到 solution.json')
"
```

### 5. 查看解决方案

生成的 `solution.json` 文件包含完整的建设方案，包括：

- 方案名称和摘要
- 综合评分（经济性、可靠性、环保性）
- 关键指标
- 各维度详细分析
- 权衡说明
- 风险评估
- 最终建议

## 输入参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 项目名称 |
| rack_count | integer | 否 | 机柜数量 |
| total_power | float | 是 | 总功率需求（kW） |
| power_density | float | 否 | 单机柜功率密度（kW/机柜） |
| tier_level | integer | 否 | 可靠性等级（1-4） |
| pue_target | float | 否 | PUE目标值 |
| floor_area | float | 否 | 建筑面积（m²） |
| green_power_ratio | float | 否 | 绿电比例（0-1） |
| budget | float | 否 | 预算上限（万元） |
| bandwidth | float | 否 | 带宽需求（Gbps） |
| objectives | array | 否 | 项目目标列表 |
| constraints | array | 否 | 约束条件列表 |
| priorities | object | 否 | 优先级设置（经济性/可靠性/环保性） |

## 输出结果说明

### 综合评分

- **overall**: 总体评分（0-1）
- **economic**: 经济性评分
- **reliability**: 可靠性评分
- **environmental**: 环保性评分

### 关键指标

- **total_cost**: 总成本（万元）
- **pue**: PUE值
- **green_power_ratio**: 绿电比例
- **tier_level**: Tier等级
- **expected_availability**: 预期可用性（%）
- **annual_carbon_emission**: 年碳排放（吨）

### 方案章节

每个维度包含：
- **description**: 方案描述
- **content**: 具体数据
- **recommendations**: 建议

### 权衡说明

描述不同维度之间的冲突及解决方案。

### 风险评估

识别潜在风险及其应对措施。

### 最终建议

提供具体的实施建议。

## 使用场景

### 场景1：初步规划

当需要快速评估数据中心建设方案的可行性和成本时：

```json
{
  "name": "新建数据中心初步规划",
  "rack_count": 50,
  "total_power": 250,
  "tier_level": 2
}
```

系统会补充缺失参数并生成初步方案。

### 场景2：方案优化

当已有基础方案，需要在不同维度间寻求平衡时：

```json
{
  "name": "数据中心方案优化",
  "rack_count": 100,
  "total_power": 500,
  "tier_level": 3,
  "pue_target": 1.3,
  "green_power_ratio": 0.8,
  "budget": 3000,
  "priorities": {
    "reliability": 5,
    "environmental": 5,
    "economic": 3
  }
}
```

系统会生成多个权衡方案供选择。

### 场景3：对比分析

生成不同参数配置下的多个方案进行对比：

```json
// 方案A：经济优先
{
  "name": "经济型数据中心方案",
  "rack_count": 100,
  "total_power": 500,
  "tier_level": 2,
  "budget": 1500
}

// 方案B：可靠优先
{
  "name": "可靠型数据中心方案",
  "rack_count": 100,
  "total_power": 500,
  "tier_level": 4,
  "budget": 3000
}
```

对比两个方案的经济性和可靠性评分。

## 系统架构

系统基于多专家协作决策架构，包含以下步骤：

1. **需求解析**: 理解用户需求，补充缺失参数
2. **专家分析**: 三个专家（经济性、可靠性、环保性）分别分析
3. **专家辩论**: 专家之间进行讨论，达成共识
4. **仲裁决策**: 综合各方意见，生成最终方案
5. **方案输出**: 输出完整的建设方案

## 常见问题

### Q: 生成一个方案需要多长时间？

A: 大约需要2-3分钟，具体取决于：
- 辩论轮数（通常1轮即可达成共识）
- 网络延迟
- API响应速度

### Q: 系统生成的方案可以直接使用吗？

A: 系统生成的是参考方案，需要：
1. 结合实际情况进行评估
2. 与专业团队讨论细节
3. 根据资源情况进行调整
4. 进行详细的工程计算和验证

### Q: 如何提高方案的经济性评分？

A: 可以尝试：
- 降低Tier等级要求
- 调整绿电比例目标
- 增加预算上限
- 明确表示经济性优先

### Q: 系统能考虑哪些约束条件？

A: 目前系统主要考虑：
- 预算约束
- 场地面积约束
- 时间约束
- 技术标准约束

特殊约束可以在 `objectives` 和 `constraints` 字段中说明。

### Q: 如果生成的方案不满意怎么办？

A: 可以：
1. 调整输入参数重新生成
2. 修改优先级设置
3. 提供更详细的约束条件
4. 多次生成选择最佳方案

### Q: 系统支持哪些语言？

A: 系统主要使用中文进行分析和输出。

## 技术支持

如有问题，请检查：

1. API密钥是否正确配置
2. 网络连接是否正常
3. 输入格式是否正确
4. 是否有足够的API配额

详细技术文档请参考：`docs/design/backend_ai_system.md`

## 更新日志

### v2.0 (2026-04-19)

- 基于LangGraph重新实现
- 添加专家辩论机制
- 改进JSON解析容错能力
- 支持流式输出
- 使用DeepSeek模型

### v1.0 (初始版本)

- 基础的多专家分析
- 简单的方案生成
