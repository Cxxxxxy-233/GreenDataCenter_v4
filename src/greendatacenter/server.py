# -*- coding: utf-8 -*-
"""
FastAPI HTTP Server - 封装 AISystemCoordinator，提供 REST API 和 SSE 实时流式输出
"""

import asyncio
import csv
import json
import mimetypes
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from greendatacenter.coordinator_v2 import AISystemCoordinator
from greendatacenter.graph.state import UserRequirement

app = FastAPI(title="数据中心绿电一体化方案智能规划系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

coordinator: Optional[AISystemCoordinator] = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_ARTIFACT_ROOTS = [
    (PROJECT_ROOT / "src" / "greendatacenter" / "output").resolve(),
    (PROJECT_ROOT / "src" / "greendatacenter" / "tools" / "csv").resolve(),
]

requirements_store: dict[str, dict] = {}
solutions_store: dict[str, dict] = {}
workflows_store: dict[str, dict] = {}
stream_queues: dict[str, asyncio.Queue] = {}


class WorkflowStartRequest(PydanticBaseModel):
    location: str = Field(..., description="数据中心所在地点")
    planned_load_kw: float = Field(..., gt=0, description="总负荷(kW)")
    green_power_ratio: float = Field(..., ge=0, le=1, description="绿电消纳率目标(0-1)")
    planned_area: float = Field(..., gt=0, description="计划建筑面积(m²)")
    budget_constraint: float = Field(..., gt=0, description="预算约束(万元)")
    cooling_technology: str = Field(default="浸没式液冷", description="制冷技术")
    machine_room_grade: str = Field(default="A", description="机房等级")
    pue_target: float = Field(default=1.3, ge=1.0, le=3.0, description="PUE目标值")
    sim_hours: int = Field(default=160, gt=0, le=8760, description="仿真时长(小时)")
    year: Optional[int] = Field(default=2025, description="气象数据年份")
    date: Optional[str] = Field(default=None, description="仿真日期")
    pv_tilt: Optional[float] = Field(default=None, description="光伏倾角(度)")
    pv_azimuth: float = Field(default=180.0, description="光伏方位角(度)")
    wind_cut_in_ms: float = Field(default=3.0, gt=0, description="风机切入风速(m/s)")
    wind_rated_ms: float = Field(default=12.0, gt=0, description="风机额定风速(m/s)")
    wind_cut_out_ms: float = Field(default=25.0, gt=0, description="风机切出风速(m/s)")
    computing_power_density: float = Field(default=8.0, gt=0, description="单机柜算力密度(kW/机柜)")
    carbon_emission_factor: float = Field(default=0.5, ge=0, description="电网碳排放因子")
    electricity_prices: dict[str, float] = Field(
        default_factory=lambda: {
            "尖峰电价": 0.5, "高峰电价": 0.4, "平段电价": 0.3,
            "低谷电价": 0.25, "深谷电价": 0.2,
        },
        description="各时段电价(元/kWh)",
    )
    maxiter: int = Field(default=60, gt=0, description="差分进化最大迭代次数")
    popsize: int = Field(default=10, gt=0, description="差分进化种群大小")
    seed: int = Field(default=42, description="随机种子")


@app.on_event("startup")
async def startup_event():
    global coordinator
    coordinator = AISystemCoordinator()


def _serialize_value(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    return value


def _make_serializable(obj: Any) -> Any:
    try:
        json.dumps(obj, ensure_ascii=False)
        return obj
    except (TypeError, ValueError, OverflowError):
        return _serialize_value(obj)


def _is_path_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _resolve_artifact_path(path_str: str) -> Path:
    if not path_str:
        raise HTTPException(status_code=400, detail="Artifact path is required")

    candidate = Path(path_str)
    if not candidate.is_absolute():
        candidate = (PROJECT_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not any(_is_path_within(candidate, root) for root in ALLOWED_ARTIFACT_ROOTS):
        raise HTTPException(status_code=403, detail="Artifact path is not allowed")

    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Artifact file not found")

    return candidate


async def _run_workflow(workflow_id: str, input_data: dict):
    queue = stream_queues.get(workflow_id)
    try:
        workflows_store[workflow_id]["status"] = "running"
        start_time = datetime.now()

        initial_state = {
            "requirement": input_data,
            "user_id": "user_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "current_step": "start",
            "next_step": "",
            "debate_round": 1,
            "max_debate_rounds": 5,
            "consensus_reached": False,
            "should_continue_debate": True,
            "budget_feedback": "",
            "budget_retry_count": 0,
            "max_budget_retries": 2,
            "draft_plan_feedback": "",
            "draft_plan_summary": "",
            "economic_opinion": None,
            "power_reliability_opinion": None,
            "environmental_opinion": None,
            "debate_history": [],
            "consensus_score": 0.0,
            "solution": {},
            "streaming_output": [],
        }

        last_node_output_with_so = None
        all_node_names_from_so = set()

        async for event in coordinator.compiled_graph.astream(initial_state):
            for node_name, node_output in event.items():
                output_keys = list(node_output.keys()) if isinstance(node_output, dict) else type(node_output).__name__
                print(f"[ASTREAM] node={node_name}, output_keys={output_keys}", flush=True)

                wf_store = workflows_store.get(workflow_id, {})
                so_list = wf_store.get("streaming_output", [])

                extracted_data = None
                if so_list:
                    for entry in reversed(so_list):
                        if isinstance(entry, dict) and entry.get("node") == node_name:
                            extracted_data = entry.get("full_output")
                            break

                if extracted_data is None:
                    if "streaming_output" in node_output and isinstance(node_output["streaming_output"], list):
                        inner_so = node_output["streaming_output"]
                        if inner_so:
                            last_node_output_with_so = node_output
                            for entry in inner_so:
                                if isinstance(entry, dict) and entry.get("node"):
                                    all_node_names_from_so.add(entry["node"])
                                    if entry.get("node") == node_name and extracted_data is None:
                                        extracted_data = entry.get("full_output")

                if extracted_data is None:
                    extracted_data = node_output

                serializable_data = _make_serializable(extracted_data)
                message = {
                    "node": node_name,
                    "data": serializable_data,
                    "timestamp": datetime.now().isoformat(),
                }
                print(f"[SSE PUSH] node={node_name}, data_keys={list(serializable_data.keys()) if isinstance(serializable_data, dict) else type(serializable_data).__name__}", flush=True)

                if queue:
                    await queue.put(message)
                if "streaming_output" in workflows_store.get(workflow_id, {}):
                    workflows_store[workflow_id]["streaming_output"].append(message)

        print("[SSE] astream loop finished", flush=True)
        print(f"[SSE] Nodes found in streaming_output: {sorted(all_node_names_from_so)}", flush=True)

        pushed_nodes = set()
        so_final = workflows_store.get(workflow_id, {}).get("streaming_output", [])
        for item in so_final:
            if isinstance(item, dict) and item.get("node"):
                pushed_nodes.add(item["node"])

        print(f"[SSE] Nodes pushed via SSE: {sorted(pushed_nodes)}", flush=True)

        missing_nodes = all_node_names_from_so - pushed_nodes
        if missing_nodes and last_node_output_with_so:
            print(f"[SSE] Missing nodes to补发: {sorted(missing_nodes)}", flush=True)
            inner_so = last_node_output_with_so.get("streaming_output", [])
            for entry in inner_so:
                if isinstance(entry, dict) and entry.get("node") in missing_nodes:
                    fallback_msg = {
                        "node": entry["node"],
                        "data": _make_serializable(entry.get("full_output", {})),
                        "timestamp": datetime.now().isoformat(),
                    }
                    print(f"[SSE FALLBACK] 补发节点: {entry['node']}, keys={list(fallback_msg['data'].keys()) if isinstance(fallback_msg['data'], dict) else 'N/A'}", flush=True)
                    if queue:
                        await queue.put(fallback_msg)
                    workflows_store[workflow_id]["streaming_output"].append(fallback_msg)
                    pushed_nodes.add(entry["node"])

        solution = {}
        for item in workflows_store.get(workflow_id, {}).get("streaming_output", []):
            node = item.get("node", "")
            data = item.get("data", {})
            if node == "arbitrator" and isinstance(data, dict):
                solution = data
            if node == "final_report" and isinstance(data, dict):
                solution.update(data)

        if "output" not in pushed_nodes:
            print("[SSE] Fallback: output node not received from astream, pushing manually", flush=True)
            fallback_output_msg = {
                "node": "output",
                "data": _make_serializable({"current_step": "completed", "final_solution": solution}),
                "timestamp": datetime.now().isoformat(),
            }
            if queue:
                await queue.put(fallback_output_msg)
            if "streaming_output" in workflows_store.get(workflow_id, {}):
                workflows_store[workflow_id]["streaming_output"].append(fallback_output_msg)
            pushed_nodes.add("output")

        streaming_output = workflows_store.get(workflow_id, {}).get("streaming_output", [])

        solution = {}
        for item in streaming_output:
            node = item.get("node", "")
            data = item.get("data", {})
            if node == "arbitrator" and isinstance(data, dict):
                solution = data
            if node == "final_report" and isinstance(data, dict):
                solution.update(data)

        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        if solution:
            solution["generation_time"] = generation_time
            solution["created_at"] = end_time.isoformat()

        result = {
            "success": True,
            "solution": _make_serializable(solution),
            "streaming_output": _make_serializable(streaming_output),
            "generation_time": generation_time,
        }

        solutions_store[workflow_id] = result
        workflows_store[workflow_id]["status"] = "completed"
        workflows_store[workflow_id]["result"] = result

        if queue:
            await queue.put({"node": "completed", "data": _make_serializable(result)})

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        traceback.print_exc()
        workflows_store[workflow_id]["status"] = "failed"
        workflows_store[workflow_id]["error"] = error_msg
        if queue:
            await queue.put({"node": "error", "data": {"error": error_msg}})


@app.post("/api/workflow/start")
async def start_workflow(request: WorkflowStartRequest):
    input_data = request.model_dump()

    req_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    requirements_store[req_id] = input_data

    workflow_id = f"wf_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    stream_queues[workflow_id] = asyncio.Queue()
    workflows_store[workflow_id] = {
        "status": "pending",
        "requirement_id": req_id,
        "streaming_output": [],
        "started_at": datetime.now().isoformat(),
    }

    asyncio.create_task(_run_workflow(workflow_id, input_data))

    return {"workflow_id": workflow_id, "requirement_id": req_id}


@app.get("/api/workflow/stream/{workflow_id}")
async def stream_workflow(workflow_id: str):
    if workflow_id not in workflows_store:
        raise HTTPException(status_code=404, detail="Workflow not found")

    async def event_generator():
        queue = stream_queues.get(workflow_id)
        if not queue:
            yield f"data: {json.dumps({'node': 'error', 'data': {'error': 'No stream queue'}}, ensure_ascii=False)}\n\n"
            return

        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=300)
                serialized = _make_serializable(item)
                yield f"data: {json.dumps(serialized, ensure_ascii=False)}\n\n"
                if item.get("node") in ("completed", "error"):
                    break
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'node': 'heartbeat'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/workflow/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    if workflow_id not in workflows_store:
        raise HTTPException(status_code=404, detail="Workflow not found")

    wf = workflows_store[workflow_id]
    return {
        "workflow_id": workflow_id,
        "status": wf.get("status", "unknown"),
        "started_at": wf.get("started_at"),
        "error": wf.get("error"),
        "streaming_output_count": len(wf.get("streaming_output", [])),
    }


@app.get("/api/requirements")
async def list_requirements():
    return [
        {"id": rid, **_make_serializable(req)}
        for rid, req in requirements_store.items()
    ]


@app.get("/api/requirements/{req_id}")
async def get_requirement(req_id: str):
    if req_id not in requirements_store:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return {"id": req_id, **_make_serializable(requirements_store[req_id])}


@app.get("/api/solutions")
async def list_solutions():
    results = []
    for sid, sol in solutions_store.items():
        entry = {
            "id": sid,
            "success": sol.get("success", False),
            "created_at": sol.get("solution", {}).get("created_at"),
            "name": sol.get("solution", {}).get("name"),
            "overall_scores": sol.get("solution", {}).get("overall_scores"),
            "key_metrics": sol.get("solution", {}).get("key_metrics"),
            "generation_time": sol.get("generation_time"),
        }
        results.append(entry)
    return results


@app.get("/api/solutions/{solution_id}")
async def get_solution(solution_id: str):
    if solution_id not in solutions_store:
        raise HTTPException(status_code=404, detail="Solution not found")

    sol = solutions_store[solution_id]
    solution_data = _make_serializable(sol.get("solution", {}))
    streaming = _make_serializable(sol.get("streaming_output", []))

    intermediate = {}
    for item in streaming:
        node = item.get("node", "")
        data = item.get("data", {})
        if node and data:
            intermediate[node] = {"full_output": data}

    expert_opinions = {}
    debate_messages = []
    for item in streaming:
        node = item.get("node", "")
        data = item.get("data", {})
        if node in ("economic_analysis", "power_reliability_analysis", "environmental_analysis"):
            expert_opinions[node] = data
        elif node == "debate_round":
            if isinstance(data, dict) and isinstance(data.get("messages"), list):
                for message in data["messages"]:
                    if isinstance(message, dict):
                        debate_messages.append(message)
            elif isinstance(data, dict):
                debate_messages.append(data)

    result = {
        "id": solution_id,
        "success": sol.get("success", False),
        "generation_time": sol.get("generation_time"),
        "streaming_output": streaming,
        "intermediate_results": intermediate,
        "debate_history": debate_messages,
        **solution_data,
    }

    return result


@app.get("/api/solutions/{solution_id}/export/markdown")
async def export_markdown(solution_id: str):
    if solution_id not in solutions_store:
        raise HTTPException(status_code=404, detail="Solution not found")

    sol = solutions_store[solution_id]
    solution = sol.get("solution", {}) or {}
    final_report = solution.get("final_report", "")
    report_path = solution.get("final_report_path")

    if (not final_report) and report_path:
        try:
            report_file = Path(report_path)
            if report_file.exists() and report_file.is_file():
                final_report = report_file.read_text(encoding="utf-8")
        except OSError:
            final_report = ""

    return {"content": final_report, "filename": f"report_{solution_id}.md"}


@app.get("/api/artifacts/file")
async def get_artifact_file(path: str, download: bool = False):
    artifact_path = _resolve_artifact_path(path)
    media_type = mimetypes.guess_type(str(artifact_path))[0] or "application/octet-stream"
    filename = artifact_path.name if download else None
    return FileResponse(
        path=str(artifact_path),
        media_type=media_type,
        filename=filename,
    )


@app.get("/api/artifacts/preview")
async def preview_artifact(path: str, limit: int = 50):
    artifact_path = _resolve_artifact_path(path)
    suffix = artifact_path.suffix.lower()
    normalized_limit = max(1, min(limit, 200))

    if suffix == ".csv":
        rows: list[list[str]] = []
        truncated = False
        with artifact_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            for index, row in enumerate(reader):
                if index >= normalized_limit:
                    truncated = True
                    break
                rows.append([str(cell) for cell in row])

        return {
            "path": str(artifact_path),
            "name": artifact_path.name,
            "type": "csv",
            "rows": rows,
            "row_count": len(rows),
            "truncated": truncated,
        }

    text_suffixes = {".txt", ".md", ".log", ".json"}
    if suffix in text_suffixes:
        content = artifact_path.read_text(encoding="utf-8")
        preview_text = content[: min(len(content), normalized_limit * 400)]
        return {
            "path": str(artifact_path),
            "name": artifact_path.name,
            "type": "text",
            "content": preview_text,
            "truncated": len(preview_text) < len(content),
        }

    return {
        "path": str(artifact_path),
        "name": artifact_path.name,
        "type": "binary",
        "preview_url": f"/api/artifacts/file?path={path}",
    }


@app.get("/api/system/status")
async def system_status():
    if coordinator is None:
        return {"status": "not_initialized"}
    return coordinator.get_system_status()


def run_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
