# 前后端衔接修改方案

## 一、核心问题诊断

经过详细代码审查，发现以下关键问题：

### 1.1 后端无API服务器（最严重问题）
- 后端只有CLI入口（`cli.py`）和Python库（`AISystemCoordinator`），**没有HTTP API服务器**
- `pyproject.toml`中`fastapi`和`uvicorn`仅作为可选依赖，未被实际使用
- 前端`api/index.js`定义的所有端点（`/requirements`、`/workflow/start`、`/solutions`等）**均不存在**

### 1.2 前端数据映射问题
- **Config.vue**: `location`字段使用英文key（如`wulanchabu`），后端期望中文（如`贵阳`）；`green_power_ratio`前端用百分比（0-100），后端期望小数（0-1）；`transformToBackendFormat`转换的字段名与后端`UserRequirement`不匹配
- **Generate.vue**: 依赖不存在的API端点（`workflowApi.startWorkflow`、`workflowApi.getStatus`）；`updateIntermediateResults`的数据路径与后端`streaming_output`结构不完全匹配
- **Detail.vue**: 从`solutionApi.getById`加载数据，但该API不存在；`intermediate_results`的访问路径假设了后端存储结构
- **Home.vue / History.vue**: 使用硬编码的假数据，`solutionApi.getAll`端点不存在

### 1.3 实时流式输出问题
- 后端`streaming_output`是列表，在图执行完成后才返回，**不支持实时推送**
- 前端`connectToLogStream`尝试连接SSE端点`/logs/stream`，但该端点不存在
- 前端`pollWorkflowStatus`轮询工作流状态，但后端无此机制

---

## 二、修改方案

### 2.1 新建后端FastAPI服务器（核心）

**文件**: `src/greendatacenter/server.py`

创建FastAPI应用，封装`AISystemCoordinator`，提供以下功能：

#### API端点设计

| 端点 | 方法 | 功能 | 对应后端方法 |
|------|------|------|-------------|
| `/api/requirements` | POST | 提交需求参数 | 保存到内存存储，返回requirement_id |
| `/api/requirements/{id}` | GET | 获取需求 | 从内存存储读取 |
| `/api/workflow/start` | POST | 启动方案生成 | `coordinator.generate_solution_async()` |
| `/api/workflow/status/{id}` | GET | 查询工作流状态 | 从内存存储读取 |
| `/api/workflow/stream/{id}` | GET(SSE) | 实时流式输出 | SSE推送streaming_output |
| `/api/solutions` | GET | 获取方案列表 | 从内存存储读取 |
| `/api/solutions/{id}` | GET | 获取方案详情 | 从内存存储读取 |
| `/api/solutions/{id}/export/markdown` | GET | 导出Markdown报告 | 返回final_report |

#### 实时流式输出方案
- 使用**后台任务**执行`coordinator.generate_solution_async()`
- 通过自定义LangGraph回调，在每个节点执行完成后将`streaming_output`推送到SSE队列
- 前端通过SSE连接`/api/workflow/stream/{id}`实时接收各节点输出

#### 内存存储方案
- 使用Python字典作为内存存储（`requirements_store`、`solutions_store`、`workflows_store`）
- 每次生成方案时，将完整的`streaming_output`和`solution`保存到对应store

### 2.2 修改前端API层

**文件**: `frontend/src/api/index.js`

修改内容：
- 更新所有API端点路径，添加`/api`前缀
- 新增`workflowApi.startDirect(data)`方法，直接提交需求参数并启动工作流（无需先提交requirement再启动workflow）
- 新增SSE连接方法`workflowApi.connectStream(workflowId)`
- 移除不存在的端点调用

### 2.3 修改Config.vue（参数配置页）

修改内容：
1. **location字段**：将`el-option`的value从英文key改为中文城市名（`"贵阳"`、`"乌兰察布"`等），与后端`UserRequirement.location`对齐
2. **green_power_ratio**：保持前端输入为百分比（0-100），在提交时除以100转为小数（0-1）
3. **transformToBackendFormat**：重写，严格对齐后端`UserRequirement`字段名：
   - 移除`name`、`description`、`owner`、`rack_count`、`tier_level`、`floor_area`、`budget`、`objectives`、`constraints`等后端不识别的字段
   - 直接使用后端字段名：`location`、`planned_load_kw`、`green_power_ratio`（小数）、`planned_area`、`budget_constraint`、`machine_room_grade`、`pue_target`、`sim_hours`、`year`、`pv_tilt`、`pv_azimuth`、`wind_cut_in_ms`、`wind_rated_ms`、`wind_cut_out_ms`、`computing_power_density`、`carbon_emission_factor`、`electricity_prices`、`maxiter`、`popsize`、`seed`
4. **移除后端不支持的参数**：`priorities`（专家决策权重）、`priority`（方案优先级）等后端`UserRequirement`中不存在的字段
5. **saveParams**：改为直接调用`workflowApi.startDirect(data)`，一步完成参数提交和工作流启动

### 2.4 修改Generate.vue（方案生成页）

修改内容：
1. **启动工作流**：改为直接POST需求参数到`/api/workflow/start`，获取`workflow_id`
2. **实时流式输出**：使用SSE连接`/api/workflow/stream/{workflow_id}`，实时接收各节点输出
3. **updateIntermediateResults**：重写数据映射逻辑，严格对齐后端`streaming_output`结构：

   后端`streaming_output`每条记录结构：
   ```json
   {
     "node": "requirement_parser|draft_plan_agent|cost_calculation|economic_analysis|power_reliability_analysis|environmental_analysis|debate|arbitrator|final_report",
     "expert": "专家名称",
     "content": "内容摘要",
     "full_output": { 完整输出数据 },
     "round": 1  // 仅辩论节点有
   }
   ```

4. **各节点数据映射**：
   - `requirement_parser` → `full_output`为`UserRequirement.model_dump()`
   - `draft_plan_agent` → `full_output.parsed`包含`green_power_result`、`cooling_result`、`power_supply_plan`
   - `cost_calculation` → `full_output`包含`is_over_budget`、`total_capex_lakh`、`capex_breakdown`
   - `economic_analysis` → `full_output`为`ExpertOpinion.model_dump()`
   - `power_reliability_analysis` → `full_output`为`ExpertOpinion.model_dump()`
   - `environmental_analysis` → `full_output`为`ExpertOpinion.model_dump()`
   - `debate` → `content`为发言内容，`expert`为发言者，`round`为轮次
   - `arbitrator` → `full_output`为仲裁结果（`overall_scores`、`key_metrics`等）
   - `final_report` → `full_output.path`为报告路径

5. **进度计算**：基于接收到的streaming_output条目数计算进度百分比
6. **专家卡片**：从`streaming_output`中提取各专家的`ExpertOpinion`，展示`scores`、`metrics`、`recommendations`、`concerns`
7. **辩论展示**：从`streaming_output`中提取`debate`类型的记录，按轮次分组展示

### 2.5 修改Detail.vue（方案详情页）

修改内容：
1. **数据加载**：从`/api/solutions/{id}`加载完整方案数据
2. **方案概览**：所有指标严格从后端`solution`对象中读取：
   - `coolingResult` ← `solution.cooling_result`（来自draft_plan_agent）
   - `greenOptimization` ← `solution.green_power_result.optimization`
   - `powerPlan` ← `solution.power_supply_plan`
   - `costResult` ← `solution.economic_analysis_result`（成本计算结果）
   - `arbitrator` ← `solution`（仲裁结果直接在solution顶层）
   - `overallScores` ← `solution.overall_scores`
   - `keyMetrics` ← `solution.key_metrics`
3. **制冷系统详情**：从`cooling_result`读取`cooling_technology`、`estimated_pue`、`predicted_wue`、`cooling_kpis`、`economic_indicators`
4. **绿电系统详情**：从`green_power_result.optimization`读取`wind_capacity_mw`、`pv_capacity_mw`、`storage_capacity_mwh`
5. **供电系统详情**：从`power_supply_plan`读取`external_voltage`、`redundancy_logic`、`bus_type`、`diesel_status`
6. **经济分析**：从`economic_analysis_result`和`economic_section`读取成本分解
7. **可靠性分析**：从`power_reliability_section`和`power_reliability_opinion`读取
8. **环保分析**：从`environmental_section`和`environmental_opinion`读取
9. **专家评审记录**：从`streaming_output`中提取专家意见和辩论记录
10. **完整方案报告**：从`solution.final_report`读取Markdown文本

### 2.6 修改Home.vue（首页）

修改内容：
1. **统计数据**：从`/api/solutions`获取真实方案数据计算统计指标
2. **最近项目**：从`/api/solutions`加载真实方案列表，映射字段：
   - `name` ← `solution.name`
   - `location` ← `solution.requirement.location`（如可用）
   - `createTime` ← `solution.created_at`
   - `status` ← 根据`solution.success`判断
   - `coreMetrics` ← `solution.key_metrics`

### 2.7 修改History.vue（历史项目页）

修改内容：
1. **项目列表**：从`/api/solutions`加载真实数据
2. **字段映射**：
   - `cabinetPower` ← `solution.key_metrics`中无此字段，改为显示`computing_power_density`或移除
   - `pue` ← `solution.key_metrics.pue`
   - `greenRate` ← `solution.key_metrics.green_power_ratio * 100`
   - `investment` ← `solution.key_metrics.total_cost`

---

## 三、实施步骤

### 步骤1：创建后端FastAPI服务器
- 新建`src/greendatacenter/server.py`
- 实现所有API端点
- 实现SSE实时流式输出
- 实现内存存储

### 步骤2：修改前端API层
- 更新`frontend/src/api/index.js`
- 对齐所有API端点路径和数据格式

### 步骤3：修改Config.vue
- 修复location字段映射
- 修复green_power_ratio转换
- 重写transformToBackendFormat
- 移除后端不支持的参数

### 步骤4：修改Generate.vue
- 重写工作流启动逻辑
- 实现SSE实时流式输出接收
- 重写updateIntermediateResults数据映射
- 修复各节点展示组件的数据绑定

### 步骤5：修改Detail.vue
- 重写数据加载逻辑
- 修复所有数据展示组件的字段映射
- 确保所有数据来自后端真实输出

### 步骤6：修改Home.vue和History.vue
- 替换硬编码数据为API调用
- 修复字段映射

### 步骤7：端到端测试
- 启动后端服务器
- 启动前端开发服务器
- 完整流程测试：配置参数 → 生成方案 → 查看详情

---

## 四、后端server.py关键设计

### 4.1 SSE实时推送方案

```python
# 在LangGraph执行过程中，通过自定义回调捕获每个节点的输出
# 使用asyncio.Queue实现SSE推送

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()
coordinator = AISystemCoordinator()

# 内存存储
requirements_store = {}
solutions_store = {}
workflows_store = {}

# SSE队列
stream_queues = {}

@app.post("/api/workflow/start")
async def start_workflow(data: dict):
    workflow_id = f"wf_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    stream_queues[workflow_id] = asyncio.Queue()
    
    # 后台执行
    asyncio.create_task(run_workflow(workflow_id, data))
    
    return {"workflow_id": workflow_id}

async def run_workflow(workflow_id: str, input_data: dict):
    # 自定义回调，在每个节点完成后推送数据
    def on_node_complete(node_name, output):
        stream_queues[workflow_id].put_nowait({
            "node": node_name,
            "data": output
        })
    
    result = await coordinator.generate_solution_async(input_data)
    
    # 保存结果
    solutions_store[workflow_id] = result
    workflows_store[workflow_id] = {"status": "completed", **result}
    
    # 发送完成信号
    await stream_queues[workflow_id].put({"node": "completed", "data": result})

@app.get("/api/workflow/stream/{workflow_id}")
async def stream_workflow(workflow_id: str):
    async def event_generator():
        queue = stream_queues.get(workflow_id)
        if not queue:
            yield f"data: {json.dumps({'error': 'Workflow not found'})}\n\n"
            return
        
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=300)
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
                if item.get("node") == "completed":
                    break
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'node': 'heartbeat'})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### 4.2 节点输出捕获方案

需要修改`AISystemCoordinator.generate_solution_async`，添加节点完成回调。**注意：不修改后端逻辑，仅添加回调钩子**。

具体方式：使用LangGraph的`astream`方法替代`ainvoke`，可以逐节点获取输出：

```python
async def generate_solution_async(self, input_data, on_node_complete=None):
    initial_state = {...}
    
    # 使用astream逐节点获取输出
    async for event in self.compiled_graph.astream(initial_state):
        # event是 {node_name: node_output} 格式
        for node_name, node_output in event.items():
            if on_node_complete:
                await on_node_complete(node_name, node_output)
    
    # 最终状态
    final_state = ...
    return result
```

---

## 五、数据映射对照表

### 5.1 前端Config → 后端UserRequirement

| 前端字段 | 后端字段 | 转换规则 |
|----------|----------|----------|
| `location` (中文) | `location` | 直接传递中文城市名 |
| `planned_load_kw` | `planned_load_kw` | 直接传递 |
| `green_power_ratio` (0-100) | `green_power_ratio` (0-1) | 除以100 |
| `planned_area` | `planned_area` | 直接传递 |
| `budget_constraint` | `budget_constraint` | 直接传递 |
| `machine_room_grade` | `machine_room_grade` | 直接传递 |
| `pue_target` | `pue_target` | 直接传递 |
| `sim_hours` | `sim_hours` | 直接传递 |
| `year` | `year` | 直接传递 |
| `pv_tilt` | `pv_tilt` | 直接传递 |
| `pv_azimuth` | `pv_azimuth` | 直接传递 |
| `wind_cut_in_ms` | `wind_cut_out_ms` | 直接传递 |
| `computing_power_density` | `computing_power_density` | 直接传递 |
| `carbon_emission_factor` | `carbon_emission_factor` | 直接传递 |
| `electricity_prices` | `electricity_prices` | 直接传递 |
| `maxiter` | `maxiter` | 直接传递 |
| `popsize` | `popsize` | 直接传递 |
| `seed` | `seed` | 直接传递 |

### 5.2 后端streaming_output → 前端Generate.vue

| 后端node名 | 前端展示区域 | 数据映射 |
|------------|-------------|----------|
| `requirement_parser` | 需求解析卡片 | `full_output.location`、`full_output.planned_load_kw`、`full_output.green_power_ratio` |
| `draft_plan_agent` | 初稿生成三卡片 | `full_output.parsed.green_power_result.optimization`→绿电卡片；`full_output.parsed.cooling_result`→制冷卡片；`full_output.parsed.power_supply_plan`→供电卡片 |
| `cost_calculation` | 成本计算卡片 | `full_output.total_capex_lakh`、`full_output.is_over_budget`、`full_output.capex_breakdown` |
| `economic_analysis` | 经济性专家卡片 | `full_output.scores`、`full_output.metrics`、`full_output.recommendations`、`full_output.concerns` |
| `power_reliability_analysis` | 可靠性专家卡片 | 同上 |
| `environmental_analysis` | 环保性专家卡片 | 同上 |
| `debate` | 辩论时间线 | `expert`→发言者、`content`→发言内容、`round`→轮次 |
| `arbitrator` | 仲裁决策卡片 | `full_output.overall_scores`、`full_output.key_metrics`、`full_output.trade_offs`、`full_output.risks` |
| `final_report` | 报告预览 | `full_output.path` |

### 5.3 后端solution → 前端Detail.vue

| 后端字段 | 前端展示位置 | 说明 |
|----------|-------------|------|
| `solution.name` | 方案概览-方案名称 | 仲裁输出的方案名 |
| `solution.summary` | 方案概览-方案摘要 | 仲裁输出的摘要 |
| `solution.overall_scores` | 方案概览-综合评分 | economic/reliability/environmental/overall |
| `solution.key_metrics` | 方案概览-关键指标 | total_cost/pue/green_power_ratio/tier_level/expected_availability/annual_carbon_emission |
| `solution.economic_section` | 经济分析Tab | description/content/recommendations |
| `solution.power_reliability_section` | 可靠性分析Tab | description/content/recommendations |
| `solution.environmental_section` | 环保分析Tab | description/content/recommendations |
| `solution.trade_offs` | 方案概览-权衡方案 | conflict/resolution |
| `solution.risks` | 方案概览-风险评估 | type/description |
| `solution.recommendations` | 方案概览-最终建议 | 字符串列表 |
| `solution.confidence` | 方案概览-置信度 | 0-1 |
| `solution.final_report` | 完整方案报告Tab | Markdown文本 |
| `streaming_output`中的专家意见 | 专家评审记录Tab | 各ExpertOpinion |
| `streaming_output`中的辩论记录 | 专家评审记录Tab | 各DebateMessage |

---

## 六、注意事项

1. **不修改后端逻辑**：仅添加`server.py`作为HTTP封装层，不修改`coordinator_v2.py`、`nodes.py`等核心文件
2. **使用`astream`替代`ainvoke`**：在`server.py`中使用LangGraph的`astream`方法实现逐节点输出，无需修改后端节点逻辑
3. **前端样式保持不变**：仅修改数据绑定和API调用，不改变页面布局和样式
4. **CORS配置**：后端需配置CORS允许前端跨域访问
5. **错误处理**：前端需优雅处理后端API调用失败的情况
