# 代码说明和开发指南

本目录包含代码说明、开发规范和贡献指南等文档。

## 开发环境设置

### 前置要求

- Python >= 3.10
- uv (现代Python包管理器)
- DeepSeek API Key

### 环境配置步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd GreenDataCenter

# 2. 安装依赖
uv sync

# 3. 配置API密钥
cp .env.example .env
# 编辑.env文件，添加DeepSeek API密钥
# .env 文件内容示例：
# LLM_API_KEY=sk-your-deepseek-api-key-here
#
# API Key 可在 https://platform.deepseek.com 获取

# 4. 激活虚拟环境
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

## 运行程序

### 基本运行方式

使用以下命令运行程序，读取输入文件并生成数据中心建设方案：

```bash
uv run python -m greendatacenter.cli generate example_input.json -o solution.json --detail full
```

**命令参数说明：**

| 参数 | 说明 |
|------|------|
| `generate` | 子命令：生成方案 |
| `example_input.json` | 输入文件路径（JSON格式） |
| `-o solution.json` | 输出文件路径，生成方案将保存到此文件 |
| `--detail full` | 输出详细程度：`summary`（摘要）、`detail`（详细）、`full`（完整） |

### 输入文件格式

项目根目录下的 `example_input.json` 是一个完整的输入示例：

```json
{
  "location": "贵阳",
  "planned_load_kw": 12000,
  "green_power_ratio": 0.6,
  "planned_area": 18000,
  "budget_constraint": 35000,
  "cooling_technology": "浸没式液冷",
  "machine_room_grade": "A",
  "pue_target": 1.25,
  "sim_hours": 168,
  "electricity_prices": {
    "尖峰电价": 0.6,
    "高峰电价": 0.5,
    "平段电价": 0.4,
    "低谷电价": 0.3,
    "深谷电价": 0.25
  }
}
```

**输入字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `location` | string | 是 | 数据中心所在城市 |
| `planned_load_kw` | float | 是 | 规划用电负荷（kW） |
| `green_power_ratio` | float | 否 | 绿电比例（0-1） |
| `planned_area` | float | 否 | 规划面积（m²） |
| `budget_constraint` | float | 否 | 预算约束（万元） |
| `cooling_technology` | string | 否 | 制冷技术（如"浸没式液冷"） |
| `machine_room_grade` | string | 否 | 机房等级（A/B/C） |
| `pue_target` | float | 否 | PUE目标值 |
| `sim_hours` | int | 否 | 仿真时长（小时） |
| `year` | int | 否 | 仿真年份 |
| `pv_tilt` | float | 否 | 光伏倾斜角度（null则自动计算） |
| `pv_azimuth` | float | 否 | 光伏方位角 |
| `wind_cut_in_ms` | float | 否 | 风电切入风速（m/s） |
| `wind_rated_ms` | float | 否 | 风电额定风速（m/s） |
| `wind_cut_out_ms` | float | 否 | 风电切出风速（m/s） |
| `computing_power_density` | float | 否 | 算力密度（kW/机柜） |
| `carbon_emission_factor` | float | 否 | 碳排放因子 |
| `electricity_prices` | object | 否 | 分时电价配置 |
| `maxiter` | int | 否 | 优化最大迭代次数 |
| `popsize` | int | 否 | 优化种群大小 |
| `seed` | int | 否 | 随机种子 |

### 其他 CLI 命令

```bash
# 生成示例输入文件
uv run python -m greendatacenter.cli example

# 查看系统状态
uv run python -m greendatacenter.cli status

# 解释已生成的方案
uv run python -m greendatacenter.cli explain solution.json --detail full
```

### 运行流程说明

程序运行时，系统会依次执行以下步骤（全程约2分钟）：

1. **需求解析** — 解析输入的JSON文件，提取关键参数
2. **经济性分析** — 经济性专家分析成本、投资回报等
3. **供电可靠性分析** — 供电可靠性专家评估可用性、冗余设计
4. **环保性分析** — 环保性专家评估PUE、碳排、绿电比例
5. **专家辩论** — 多轮专家讨论，达成共识
6. **仲裁决策** — 综合各方意见，生成平衡方案
7. **方案输出** — 保存完整方案到指定JSON文件

运行过程中，终端会实时输出各专家的分析内容。方案生成成功后，结果会保存到 `-o` 参数指定的文件中。

### 运行注意事项

- **API密钥必须配置**：运行前确保 `.env` 文件中 `LLM_API_KEY` 已正确设置，否则会报 `缺少环境变量 LLM_API_KEY` 错误
- **网络连接**：程序需要访问 DeepSeek API，请确保网络通畅
- **生成时间**：一次完整方案生成约需 1-3 分钟，取决于 API 响应速度
- **JSON解析容错**：如果LLM返回的JSON格式异常，系统会自动使用默认值继续运行

### IDE配置

推荐使用以下IDE：

- **VSCode**: 安装Python扩展
- **PyCharm**: 配置Python解释器
- **Jupyter**: 用于交互式开发

## 项目结构

```
GreenDataCenter/
├── src/greendatacenter/        # 源代码
│   ├── __init__.py
│   ├── coordinator_v2.py         # AI系统协调器
│   ├── cli.py                    # CLI接口
│   ├── llm/                      # LLM配置
│   ├── memory/                   # 记忆模块
│   └── graph/                    # LangGraph相关
│       ├── state.py               # 图状态定义
│       ├── nodes.py               # 节点函数
│       ├── edges.py               # 边和条件函数
│       └── build.py               # 图构建器
├── tests/                        # 测试代码
├── docs/                         # 文档
├── data/                         # 数据文件
└── pyproject.toml              # 项目配置
```

## 开发规范

### 命名规范

- **文件名**: 使用蛇形命名法（snake_case）
- **类名**: 使用帕斯卡命名法（PascalCase）
- **函数名**: 使用蛇形命名法
- **常量**: 使用大写字母+下划线（UPPER_CASE）
- **模块名**: 使用小写字母

### 代码风格

- **缩进**: 4个空格
- **行长**: 每行不超过100字符
- **空行**: 2行空行分隔
- **注释**: 使用中文注释，关键逻辑添加说明

### 文档字符串

```python
"""
模块或类的文档字符串。

Args:
    arg1: 参数1说明
    arg2: 参数2说明

Returns:
    返回值类型和说明

Raises:
    异常类型和触发条件

Example:
    使用示例
"""
```

### 类型注解

```python
from typing import Any, Optional, Dict, List

def generate_solution(
    input_data: Dict[str, Any],
    on_stream_chunk: Optional[callable] = None
) -> Dict[str, Any]:
    """生成解决方案

    Args:
        input_data: 用户输入数据
        on_stream_chunk: 流式输出回调

    Returns:
        包含success、solution等字段的字典
    """
    pass
```

### 错误处理

```python
def process_data(data: dict) -> dict:
    """处理数据

    Args:
        data: 输入数据

    Returns:
        处理后的数据

    Raises:
        ValueError: 数据格式错误时
    """
    if not data:
        raise ValueError("数据不能为空")

    # 处理逻辑
    return processed_data
```

## 测试

### 测试目录结构

```
tests/
├── README.md                  # 测试说明
├── test_api.py                # API测试
├── test_simple.py             # 导入测试
├── test_coordinator.py         # 完整功能测试
└── test_save_solution.py       # 方案保存测试
```

### 运行测试

```bash
# 运行所有测试
cd tests
for test_file in test_*.py; do
    uv run python "$test_file"
done

# 运行特定测试
uv run python tests/test_coordinator.py

# 查看测试覆盖率
pytest --cov=src/greendatacenter --cov-report=html
```

### 测试编写规范

- 测试文件名以 `test_` 开头
- 测试函数名以 `test_` 开头
- 每个测试一个断言
- 使用有意义的变量名
- 添加测试文档

```python
def test_coordinator_creation():
    """测试协调器创建"""
    coordinator = AISystemCoordinator()
    assert coordinator is not None
    assert coordinator.graph is not None
```

## 调试

### 日志配置

使用Python标准logging模块：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### 断点调试

在IDE中设置断点：
```python
# VSCode
# 在代码行号左侧点击设置断点

# PyCharm
# 在代码行号左侧点击设置断点
```

### 常见问题排查

1. **导入错误**
   - 检查PYTHONPATH
   - 确认虚拟环境已激活
   - 检查__init__.py是否正确

2. **API连接失败**
   - 检查.env文件
   - 验证API密钥
   - 检查网络连接

3. **JSON解析失败**
   - 查看LLM输出格式
   - 检查解析器容错逻辑

## 部署

### 本地部署

```bash
# 安装依赖
uv sync

# 设置环境变量
export LLM_API_KEY=your_api_key_here

# 运行服务
uv run python -m greendatacenter.server
```

### Docker部署（计划中）

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install uv && \
    uv sync

EXPOSE 8000

CMD ["python", "-m", "greendatacenter.server"]
```

### 云部署（计划中）

支持主流云平台：
- 阿里云
- 腾讯云
- AWS
- Google Cloud

## 贡献指南

### 代码贡献流程

1. Fork项目
2. 创建特性分支
3. 进行开发
4. 添加测试
5. 提交PR
6. 代码审查

### 提交规范

```bash
# 提交前检查
uv run pytest

# 提交信息格式
git commit -m "feat: 添加新功能
git commit -m "fix: 修复bug
git commit -m "docs: 更新文档"
```

### Pull Request规范

PR标题格式：
- `feat: 简短描述`
- `fix: 修复bug描述`
- `docs: 文档更新`
- `refactor: 代码重构`

PR描述应包含：
- 变更说明
- 测试情况
- 相关issue

## 版本管理

### 语义化版本

版本号格式：`v主版本.次版本.修订版本`

示例：
- `v1.0.0` - 初始版本
- `v1.1.0` - 添加新功能
- `v1.1.1` - 修复bug
- `v2.0.0` - 重大版本更新

### 发布检查清单

- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 文档更新
- [ ] 更新日志更新
- [ ] 版本号更新
- [ ] 标签创建

## 性能优化

### 代码优化

- 使用异步IO减少等待时间
- 避免不必要的API调用
- 使用缓存机制
- 优化数据库查询

### 内存优化

- 及时释放大对象
- 使用生成器替代列表
- 优化字符串拼接

## 安全考虑

### API密钥管理

- 使用环境变量存储API密钥
- 不在代码中硬编码密钥
- 使用.env.example作为模板

### 数据验证

- 验证所有用户输入
- 使用Pydantic进行类型检查
- 设置合理的参数范围

### 错误信息

- 不暴露敏感信息
- 提供有用的错误消息
- 记录完整的错误堆栈
