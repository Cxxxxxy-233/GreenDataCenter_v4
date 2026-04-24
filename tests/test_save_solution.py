# -*- coding: utf-8 -*-
"""
Test coordinator and save solution to JSON
"""

import sys
import json
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from greendatacenter import AISystemCoordinator

# Create coordinator
coordinator = AISystemCoordinator()

# Test input
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

# Generate solution
print("Generating solution...")
result = coordinator.generate_solution(input_data=input_data)

if result.get("success"):
    solution = result.get("solution", {})

    # Save to JSON file
    output_file = "solution.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(solution, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Solution saved to: {output_file}")
    print(f"Solution name: {solution.get('name', 'N/A')}")
    print(f"Overall score: {solution.get('overall_scores', {}).get('overall', 0):.2f}")
    print(f"Confidence: {solution.get('confidence', 0):.2f}")
else:
    print(f"[ERROR] Failed to generate solution: {result.get('error', 'Unknown error')}")
