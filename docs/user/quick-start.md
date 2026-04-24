# 快速开始 - 启动和测试指南

本文档提供系统启动和手动测试的详细步骤。

## 环境准备

### 1. 检查Python版本

```bash
python --version
```

确保Python版本 >= 3.10

### 2. 安装依赖

```bash
# 使用uv安装依赖
uv sync

# 验证安装
uv run python --version
```

### 3. 配置API密钥

```bash
# 编辑.env文件
# 必须设置 LLM_API_KEY 变量
# 这里设置的是DeepSeek API密钥，用于调用DeepSeek模型
LLM_API_KEY=sk-your-api-key-here
```

`.env` 文件示例：
```env
# DeepSeek API Key for LLM
LLM_API_KEY=sk-your-api-key-here

# Optional: Tavily API Key for search
TAVILY_API_KEY=your_tavily_api_key_here
```

## 测试步骤

### 测试1：API连接测试

验证DeepSeek API是否可以正常连接。

```bash
uv run python tests\test_api.py
```

**预期输出**：
```
Response: OK
```

如果失败，请检查：
- API密钥是否正确
- 网络连接是否正常
- API额度是否充足

### 测试2：简单导入测试

验证所有模块可以正确导入。

```bash
uv run python tests\test_simple.py
```

**预期输出**：
```
tests/ing imports...
[OK] LLM config imported
[OK] Memory imported
[OK] Graph state imported
[OK] Nodes imported
[OK] Edges imported
[OK] Graph builder imported
[OK] Coordinator imported

All imports successful!
```

### 测试3：完整功能测试

运行完整的功能测试，生成一个数据中心建设方案。

```bash
uv run python tests\test_coordinator.py
```

**预期输出**：
```
Test 1: Creating coordinator...
AI系统协调器初始化完成
图节点: ['requirement_parser', 'economic_analysis', 'power_reliability_analysis', 'environmental_analysis', 'debate_round', 'arbitrator', 'output']
[OK] Coordinator created successfully

Test 2: Getting system status...
[OK] System status retrieved
  Coordinator version: 2.0
  Nodes: [...]
  ...

Test 3: Generating solution...
[运行过程输出...]

[OK] Solution generated successfully
  Name: [方案名称]
  Overall score: [评分]
  Generation time: [耗时]s
```

### 测试4：方案生成和保存

生成方案并保存到JSON文件。

```bash
uv run python tests\test_save_solution.py
```

**预期输出**：
```
AI系统协调器初始化完成
图节点: [...]
Generating solution...
[运行过程输出...]

[OK] Solution saved to: solution.json
Solution name: [方案名称]
Overall score: [评分]
Confidence: [置信度]
```

检查生成的 `solution.json` 文件，确保：
- 文件存在且可读
- JSON格式正确
- 包含所有必需字段

## 手动测试用例

### 用例1：基础方案生成

**目标**：生成一个基础的数据中心建设方案

**输入数据**：
```json
{
  "name": "测试数据中心",
  "rack_count": 50,
  "total_power": 250,
  "tier_level": 2
}
```

**预期结果**：
- 成功生成方案
- 方案包含所有必需字段
- 综合评分在合理范围内（0.5-0.95）

### 用例2：高可靠性方案

**目标**：生成高可靠性的数据中心方案

**输入数据**：
```json
{
  "name": "高可靠性数据中心",
  "rack_count": 100,
  "total_power": 500,
  "tier_level": 4,
  "pue_target": 1.5,
  "green_power_ratio": 0.8,
  "budget": 5000,
  "priorities": {
    "reliability": 5,
    "economic": 3,
    "environmental": 3
  }
}
```

**预期结果**：
- 可靠性评分 > 0.9
- Tier级别为4
- 预期可用性 > 99.99%

### 用例3：绿色环保方案

**目标**：生成环保优先的数据中心方案

**输入数据**：
```json
{
  "name": "绿色数据中心",
  "rack_count": 100,
  "total_power": 500,
  "tier_level": 3,
  "pue_target": 1.2,
  "green_power_ratio": 0.9,
  "budget": 3000,
  "priorities": {
    "environmental": 5,
    "reliability": 4,
    "economic": 3
  }
}
```

**预期结果**：
- 环保性评分 > 0.85
- PUE值 <= 1.3
- 绿电比例 >= 0.8
- 年碳排放较低

### 用例4：经济性优先方案

**目标**：生成经济优先的数据中心方案

**输入数据**：
```json
{
  "name": "经济型数据中心",
  "rack_count": 100,
  "total_power": 500,
  "tier_level": 2,
  "pue_target": 1.8,
  "green_power_ratio": 0.3,
  "budget": 1500,
  "priorities": {
    "economic": 5,
    "reliability": 3,
    "environmental": 2
  }
}
```

**预期结果**：
- 经济性评分 > 0.8
- 总成本较低
- ROI较高

## 性能基准

### 正常性能指标

- **API连接时间**: < 5秒
- **需求解析**: < 20秒
- **专家分析（3个）**: 60-90秒
- **专家辩论**: 10-30秒（通常1轮）
- **仲裁决策**: 30-50秒
- **总生成时间**: 100-180秒

### 异常情况处理

如果遇到以下情况：

1. **生成时间 > 5分钟**
   - 检查网络连接
   - 检查API响应时间
   - 可能需要减少max_debate_rounds

2. **JSON解析失败**
   - 检查LLM输出格式
   - 系统会自动尝试多种解析策略
   - 查看日志中的警告信息

3. **评分异常（< 0.5 或 > 1.0）**
   - 检查输入参数是否合理
   - 重新生成方案
   - 查看专家意见是否一致

## 故障排查

### 常见问题

#### 1. ModuleNotFoundError

```
ModuleNotFoundError: No module named 'langchain'
```

**解决方法**：
```bash
uv sync
```

#### 2. ImportError

```
ImportError: cannot import name 'XXX' from 'langgraph.graph'
```

**解决方法**：
- 检查LangGraph版本：`uv run python -c "import langgraph; print(langgraph.__version__)"`
- 如果版本不匹配，重新同步：`uv sync`

#### 3. API连接失败

```
openai.AuthenticationError: Error code: 401
```

**解决方法**：
- 检查`.env`文件中的API密钥
- 验证API密钥是否有效
- 检查API额度是否充足

#### 4. UnicodeEncodeError

```
UnicodeEncodeError: 'gbk' codec can't encode character
```

**说明**：这是Windows控制台编码问题，不影响功能

**解决方法**：
- 忽略控制台显示的乱码
- 查看生成的JSON文件，内容是正确的
- 或者使用UTF-8编码的终端

#### 5. JSON解析失败

```
pydantic_core._pydantic_core.ValidationError
```

**解决方法**：
- 系统会自动使用默认值继续
- 检查LLM输出格式
- 查看日志中的警告信息

## 质量检查清单

运行测试后，使用以下清单验证系统：

### 功能完整性

- [ ] API连接正常
- [ ] 所有模块导入成功
- [ ] 需求解析正常
- [ ] 三个专家分析正常
- [ ] 专家辩论正常
- [ ] 仲裁决策正常
- [ ] 方案输出正常

### 输出质量

- [ ] 方案名称有意义
- [ ] 方案摘要清晰
- [ ] 综合评分合理（0.5-0.95）
- [ ] 关键指标完整
- [ ] 各维度分析详细
- [ ] 权衡说明合理
- [ ] 风险评估充分
- [ ] 最终建议可执行

### 文件正确性

- [ ] JSON文件格式正确
- [ ] 所有必需字段存在
- [ ] 数据类型正确
- [ ] 中文显示正常（在JSON文件中）

## 下一步

完成测试后，可以：

1. 查看生成的方案，评估质量
2. 根据实际需求调整输入参数
3. 尝试不同的优先级设置
4. 对比不同参数配置的结果

详细使用说明请参考 [用户指南](../user_guide.md)。
