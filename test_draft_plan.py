import sys
sys.path.insert(0, 'src')

from greendatacenter.graph.nodes import DraftPlanAgentNode
from greendatacenter.memory import ExpertSharedMemory

# 测试工具调用
memory = ExpertSharedMemory()
agent = DraftPlanAgentNode(memory)

# 创建测试状态
test_state = {
    'user_requirement': {
        'location': '乌兰察布',
        'planned_load_kw': 500,
        'green_power_ratio': 0.7,
        'pue_target': 1.3,
        'computing_power_density': 8.0,
        'priority': 'economic'
    },
    'streaming_output': []
}

# 执行测试
result = agent(test_state)
print('=== 测试结果 ===')
print(f'green_power_result exists: {bool(result.get("green_power_result"))}')
print(f'cooling_result exists: {bool(result.get("cooling_result"))}')
print(f'power_supply_plan exists: {bool(result.get("power_supply_plan"))}')

if result.get('green_power_result'):
    print(f'green_power_result keys: {list(result["green_power_result"].keys())}')
    if 'optimization' in result['green_power_result']:
        print(f'optimization keys: {list(result["green_power_result"]["optimization"].keys())}')

if result.get('cooling_result'):
    print(f'cooling_result keys: {list(result["cooling_result"].keys())}')

if result.get('power_supply_plan'):
    print(f'power_supply_plan keys: {list(result["power_supply_plan"].keys())}')
