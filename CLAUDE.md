# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project Name:** GreenDataCenter - 数据中心建设方案设计和推荐系统

**Project Description:**
多专家协同决策的AI系统，通过经济性、供电可靠性和环保性三个领域专家的分析、辩论和仲裁，生成数据中心建设方案。系统基于LangGraph实现顺序式专家分析流程。

## Technology Stack

- **Language:** Python 3.10+
- **Dependency Management:** uv
- **LLM Framework:** LangChain
- **Orchestration:** LangGraph (StateGraph for workflow management)
- **AI Model:** DeepSeek API (https://api.deepseek.com)

## Common Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Copy and configure environment variables
cp .env.example .env
# Edit .env to add LLM_API_KEY
```

### Running Tests
```bash
# Basic import test
uv run python tests/test_simple.py

# API connectivity test
uv run python tests/test_api.py

# Full system integration test (takes ~110 seconds)
uv run python tests/test_coordinator.py

# Solution generation and save test
uv run python tests/test_save_solution.py

# Environment variable test
uv run python tests/test_env.py

# DeepSeek model test
uv run python tests/test_deepseek.py
```

### Running the System
```bash
# Generate example input
gdc example

# Generate solution from input file
gdc generate input.json -o solution.json --detail full

# Check system status
gdc status

# Explain a generated solution
gdc explain solution.json --detail full
```

### Python API Usage
```python
import sys
sys.path.insert(0, 'src')
from greendatacenter import AISystemCoordinator

coordinator = AISystemCoordinator()
result = coordinator.generate_solution(input_data={...})
```

## Architecture

### LangGraph State-Based Workflow

The system uses LangGraph's StateGraph to orchestrate a sequential workflow:

1. **Requirement Analysis**: Parse user input and validate requirements
2. **Sequential Expert Analysis** (economic → reliability → environmental)
3. **Expert Debate**: Multi-round discussion until consensus
4. **Arbitration**: Synthesize opinions and generate final solution

### Key Design Decision: Sequential vs Parallel Execution

**Original Design**: Parallel expert execution for efficiency
**Actual Implementation**: Sequential execution (economic → reliability → environmental)
**Reason**: Parallel execution with streaming output caused JSON parsing errors when multiple LLMs wrote simultaneously
**Tradeoff**: Execution time ~110 seconds, but parsing reliability significantly improved

### Expert System Configuration

Each expert uses different temperature settings:
- Economic Analysis: 0.5 (balanced creativity and stability)
- Power Reliability: 0.3 (focused on accuracy and determinism)
- Environmental: 0.4 (balanced analysis and creativity)

### Shared Memory System

Experts access a shared memory manager (`src/greendatacenter/memory/memory_manager.py`) to:
- View other experts' analyses
- Track debate conversation history
- Provide context for arbitration decisions

### Robust JSON Parsing

The system implements a 4-tier fallback strategy in `src/greendatacenter/graph/nodes.py`:
1. Direct JSON.parse()
2. Regex extraction
3. Stack-based parsing
4. Default values with warnings

This handles LLM output format instability and ensures system continues even with malformed responses.

### Core Components

- **`coordinator_v2.py`**: Main AISystemCoordinator that builds and executes the LangGraph
- **`graph/state.py`**: State definition with TypedDict for type safety
- **`graph/nodes.py`**: All node functions (RequirementAnalyzer, ExpertNodes, DebateRound, Arbitrator)
- **`graph/edges.py`**: Conditional edges and routing logic
- **`graph/build.py`**: StateGraph construction
- **`llm/config.py`**: LLM configuration with different temperatures per expert
- **`memory/memory_manager.py`**: Shared memory for expert communication

### Output Format

System outputs a structured JSON with:
- Overall scores (economic, reliability, environmental, overall)
- Key metrics (cost, PUE, green power ratio, tier level, availability, carbon emission)
- Detailed sections per dimension
- Trade-offs, risks, and recommendations
- Confidence level

## Important Constraints

1. **All prompts require English field names** to avoid parsing issues with Chinese/English mixing
2. **UTF-8 encoding** is required in all source files
3. **Absolute imports** only (`from greendatacenter...`) - no relative imports
4. **TTY detection** for UTF-8 console output wrapper - only applies in interactive mode
5. **Sequential expert execution** - do not change to parallel without addressing JSON parsing issues

## Performance Metrics

- Average solution generation time: ~110 seconds
- Success rate: >95%
- Consensus typically achieved in 1 round (consensus level 0.8-0.97)
- API calls per solution: 4-7

## Domain Knowledge Reference

See `docs/domain/` for detailed standards:
- `tier-standards.md`: Data center tier classification (Tier I-IV)
- `pue-standards.md`: PUE calculation and optimization strategies
- `power-standards.md`: Power supply architecture and requirements
- `cooling-standards.md`: Cooling systems and technologies
