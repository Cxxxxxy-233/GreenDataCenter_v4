# GreenDataCenter 测试套件

## 测试文件说明

本目录包含所有测试文件，用于验证系统功能。

## 测试文件列表

### 1. 基础测试

| 文件名 | 状态 | 说明 |
|---------|------|------|
| test_api.py | ✅ | API连接测试 |
| test_env.py | ✅ | 环境变量测试 |
| test_deepseek.py | ✅ | DeepSeek模型测试 |
| test_simple.py | ✅ | 模块导入测试 |

### 2. 功能测试

| 文件名 | 状态 | 说明 |
|---------|------|------|
| test_coordinator.py | ✅ | 协调器完整功能测试 |
| test_save_solution.py | ✅ | 方案生成和保存测试 |

## 运行所有测试

### 测试1：验证基础环境

```bash
# 1. API连接测试
uv run python tests/test_api.py

# 2. 环境变量测试
uv run python tests/test_env.py

# 3. 模型测试
uv run python tests/test_deepseek.py
```

**预期结果**：所有基础测试通过

### 测试2：验证核心功能

```bash
# 1. 导入测试
uv run python tests/test_simple.py

# 2. 完整功能测试
uv run python tests/test_coordinator.py
```

**预期结果**：
- 模块导入成功
- 协调器创建成功
- 方案生成成功
- 生成时间 < 3分钟
- 综合评分在合理范围（0.7-0.95）

### 测试3：验证方案生成和保存

```bash
uv run python tests/test_save_solution.py
```

**预期结果**：
- 方案生成成功
- solution.json文件创建成功
- JSON格式正确
- 文件可以正常读取

## 测试报告模板

运行完整测试后，可以填写以下测试报告：

### 测试环境
- Python版本: [版本]
- 操作系统: [Windows/Linux/macOS]
- 测试时间: [日期时间]

### 测试结果

#### 基础测试
- [ ] test_api.py - API连接测试通过
- [ ] test_env.py - 环境变量测试通过
- [ ] test_deepseek.py - DeepSeek模型测试通过
- [ ] test_simple.py - 导入测试通过

#### 功能测试
- [ ] test_coordinator.py - 完整功能测试通过
- [ ] test_save_solution.py - 方案生成和保存测试通过

### 性能指标

- API响应时间: [秒]
- 需求解析时间: [秒]
- 专家分析时间: [秒]
- 辩论轮数: [轮数]
- 总生成时间: [秒]
- 生成时间效率: [每秒处理的请求数]

### 发现的问题

[记录测试过程中发现的任何问题]

### 改进建议

[基于测试结果提出改进建议]

## 快速验证命令

### 验证安装

```bash
# 检查依赖
uv sync

# 检查Python版本
python --version
```

### 验证API配置

```bash
# 检查环境变量
uv run python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('LLM_API_KEY', 'Not set'))"
```

### 运行单个测试

```bash
# API测试
uv run python tests/test_api.py

# 导入测试
uv run python tests/test_simple.py

# 完整测试
uv run python tests/test_coordinator.py
```

### 清理测试输出

```bash
# 删除生成的测试文件
rm -f solution.json test_output.txt

# 清理Python缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## 持续集成

测试应该集成到CI/CD流程中：
1. GitHub Actions或其他CI服务
2. 自动运行所有测试
3. 自动生成测试报告
4. 代码覆盖率报告

## 添加新测试

当添加新功能时，应该：

1. 在tests目录创建对应的测试文件
2. 更新本README.md文件
3. 确保测试覆盖正常流程和异常情况
4. 使用清晰的命名约定（test_<feature>.py）
5. 提供详细的测试说明和预期结果
