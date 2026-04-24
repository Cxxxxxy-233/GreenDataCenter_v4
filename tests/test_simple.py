# -*- coding: utf-8 -*-
"""
Simple test to debug
"""

import sys
sys.path.insert(0, 'src')

# Don't modify stdout for now
# Test basic imports first
print("Testing imports...")

try:
    from greendatacenter.llm.config import get_llm
    print("[OK] LLM config imported")

    from greendatacenter.memory import ExpertSharedMemory
    print("[OK] Memory imported")

    from greendatacenter.graph.state import GraphState
    print("[OK] Graph state imported")

    from greendatacenter.graph.nodes import RequirementParserNode
    print("[OK] Nodes imported")

    from greendatacenter.graph.edges import should_continue_debate
    print("[OK] Edges imported")

    from greendatacenter.graph.build import build_data_center_graph
    print("[OK] Graph builder imported")

    from greendatacenter import AISystemCoordinator
    print("[OK] Coordinator imported")

except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll imports successful!")
