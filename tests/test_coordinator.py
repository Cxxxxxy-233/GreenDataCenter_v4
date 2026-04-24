# -*- coding: utf-8 -*-
"""
Test coordinator directly
"""

import sys
import os

# 获取当前脚本所在目录的上一级目录下的 src 文件夹的绝对路径，并加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from greendatacenter import AISystemCoordinator

# Test 1: Create coordinator
print("Test 1: Creating coordinator...")
try:
    coordinator = AISystemCoordinator()
    print("[OK] Coordinator created successfully")
except Exception as e:
    print(f"[ERROR] Failed to create coordinator: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Get system status
print("\nTest 2: Getting system status...")
try:
    status = coordinator.get_system_status()
    print(f"[OK] System status retrieved")
    print(f"  Coordinator version: {status['coordinator']['version']}")
    print(f"  Nodes: {status['graph']['nodes']}")
except Exception as e:
    print(f"[ERROR] Failed to get status: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Generate solution with example input
print("\nTest 3: Generating solution...")
try:
    input_data = {
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

    result = coordinator.generate_solution(input_data=input_data)

    if result.get("success"):
        solution = result.get("solution", {})
        print(f"\n[OK] Solution generated successfully")
        print(f"  Name: {solution.get('name', 'N/A')}")
        print(f"  Overall score: {solution.get('overall_scores', {}).get('overall', 0):.2f}")
        print(f"  Generation time: {result.get('generation_time', 0):.2f}s")
    else:
        print(f"[ERROR] Failed to generate solution: {result.get('error', 'Unknown error')}")

except Exception as e:
    print(f"[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("All tests completed!")
print("="*60)
