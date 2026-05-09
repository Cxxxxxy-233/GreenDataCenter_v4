import sys, json
sys.path.insert(0, "src")
from greendatacenter.tools import plan_green_power_allocation

result = plan_green_power_allocation(
    location="北京",
    green_power_ratio=0.3,
    load_mw=10.0,
    sim_hours=24,
    date="2025-06-21",
    maxiter=20,
    popsize=8,
)

print(json.dumps(result, ensure_ascii=False, indent=2))
