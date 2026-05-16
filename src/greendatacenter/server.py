# -*- coding: utf-8 -*-
"""
FastAPI HTTP Server - 闂備浇顕х换鎰崲鐎ｎ€㈠綊宕堕?AISystemCoordinator闂傚倷鐒︾€笛呯矙閹达箑瀚夋い鎺戝暔娴滅懓霉閿濆懏璐￠柣?REST API 闂?SSE 闂備浇顕ф绋匡耿闁秴纾婚柣鎰▕濞撳鏌涚仦缁㈠殧閻熸瑥瀚刊鎾煕濠靛嫬鍔ゆい銏犳嚇閺屸剝寰勬繝鍕杸闂佺懓鎲￠幃鍌氱暦?
"""

import asyncio
import csv
import json
import mimetypes
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from xml.sax.saxutils import escape

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    LongTable,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    TableStyle,
)

from greendatacenter.coordinator_v2 import AISystemCoordinator
from greendatacenter.graph.nodes import RequirementParserNode
from greendatacenter.graph.state import UserRequirement

app = FastAPI(title="Green Data Center API", version="1.0.0")

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
registerFont(UnicodeCIDFont("STSong-Light"))


class WorkflowStartRequest(PydanticBaseModel):
    location: str = Field(..., description="Location")
    planned_load_kw: float = Field(..., gt=0, description="Total load (kW)")
    green_power_ratio: float = Field(..., ge=0, le=1, description="Green power ratio (0-1)")
    planned_area: float = Field(..., gt=0, description="Planned area (m^2)")
    budget_constraint: float = Field(..., gt=0, description="Budget constraint (10k CNY)")
    cooling_technology: str = Field(default="Immersion liquid cooling", description="Cooling technology")
    machine_room_grade: str = Field(default="A", description="Machine room grade")
    pue_target: float = Field(default=1.3, ge=1.0, le=3.0, description="PUE target")
    sim_hours: int = Field(default=160, gt=0, le=8760, description="Simulation hours")
    year: Optional[int] = Field(default=2025, description="Weather data year")
    date: Optional[str] = Field(default=None, description="Simulation date")
    pv_tilt: Optional[float] = Field(default=None, description="PV tilt (deg)")
    pv_azimuth: float = Field(default=180.0, description="PV azimuth (deg)")
    wind_cut_in_ms: float = Field(default=3.0, gt=0, description="Wind cut-in speed (m/s)")
    wind_rated_ms: float = Field(default=12.0, gt=0, description="Wind rated speed (m/s)")
    wind_cut_out_ms: float = Field(default=25.0, gt=0, description="Wind cut-out speed (m/s)")
    computing_power_density: float = Field(default=8.0, gt=0, description="Computing density (kW per rack)")
    carbon_emission_factor: float = Field(default=0.5, ge=0, description="Carbon emission factor")
    electricity_prices: dict[str, float] = Field(
        default_factory=lambda: {
            "peak": 0.5,
            "high": 0.4,
            "flat": 0.3,
            "valley": 0.25,
            "deep_valley": 0.2,
        },
        description="Time-of-use prices (CNY/kWh)",
    )
    maxiter: int = Field(default=60, gt=0, description="Max optimization iterations")
    popsize: int = Field(default=10, gt=0, description="Optimization population size")
    seed: int = Field(default=42, description="Random seed")

@app.on_event("startup")
async def startup_event():
    global coordinator
    coordinator = AISystemCoordinator()


def _serialize_value(value: Any, seen: set[int] | None = None, depth: int = 0) -> Any:
    if seen is None:
        seen = set()

    if depth > 20:
        return "<max-depth-reached>"

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    obj_id = id(value)
    if obj_id in seen:
        return "<circular-reference>"

    if hasattr(value, "model_dump"):
        seen.add(obj_id)
        try:
            dumped = value.model_dump()
            return _serialize_value(dumped, seen, depth + 1)
        finally:
            seen.discard(obj_id)

    if isinstance(value, (list, tuple)):
        seen.add(obj_id)
        try:
            return [_serialize_value(v, seen, depth + 1) for v in value]
        finally:
            seen.discard(obj_id)

    if isinstance(value, dict):
        seen.add(obj_id)
        try:
            return {
                str(k): _serialize_value(v, seen, depth + 1)
                for k, v in value.items()
            }
        finally:
            seen.discard(obj_id)

    if isinstance(value, Path):
        return str(value)

    return str(value)


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


def _load_report_markdown_from_solution(sol: dict) -> str:
    solution = sol.get("solution", {}) or {}
    final_report = solution.get("final_report", "") or ""

    candidate_paths: list[str] = []
    direct_path = solution.get("final_report_path")
    if direct_path:
        candidate_paths.append(str(direct_path))

    for item in sol.get("streaming_output", []) or []:
        if not isinstance(item, dict) or item.get("node") != "final_report":
            continue
        data = item.get("data", {}) or {}
        if isinstance(data, dict):
            inline_report = data.get("final_report")
            if inline_report:
                final_report = str(inline_report)
                break

            for maybe_path in (
                data.get("final_report_path"),
                data.get("path"),
                ((data.get("full_output") or {}).get("path") if isinstance(data.get("full_output"), dict) else None),
            ):
                if maybe_path:
                    candidate_paths.append(str(maybe_path))

    if final_report:
        return final_report

    for report_path in candidate_paths:
        try:
            report_file = Path(report_path)
            if report_file.exists() and report_file.is_file():
                return report_file.read_text(encoding="utf-8")
        except OSError:
            continue

    return ""


def _sanitize_export_filename(value: str, fallback: str) -> str:
    text = re.sub(r"[\\/:*?\"<>|]+", "_", str(value or "").strip())
    text = re.sub(r"\s+", "_", text).strip("._")
    return text or fallback


def _markdown_inline_to_reportlab(text: str) -> str:
    escaped = escape(str(text or ""))
    escaped = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"\*(.+?)\*", r"<i>\1</i>", escaped)
    return escaped


def _is_markdown_table_separator(line: str) -> bool:
    stripped = line.strip().strip("|").strip()
    if not stripped:
        return False
    return bool(re.fullmatch(r"[:\-\s|]+", stripped))


def _parse_markdown_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _build_pdf_styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="STSong-Light",
            fontSize=20,
            leading=26,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#10241a"),
            spaceAfter=10,
        ),
        "meta": ParagraphStyle(
            "ReportMeta",
            parent=base["Normal"],
            fontName="STSong-Light",
            fontSize=9.5,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#55655e"),
            spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "Heading1Pdf",
            parent=base["Heading1"],
            fontName="STSong-Light",
            fontSize=17,
            leading=23,
            textColor=colors.HexColor("#123126"),
            spaceBefore=10,
            spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "Heading2Pdf",
            parent=base["Heading2"],
            fontName="STSong-Light",
            fontSize=14,
            leading=20,
            textColor=colors.HexColor("#174032"),
            spaceBefore=8,
            spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "Heading3Pdf",
            parent=base["Heading3"],
            fontName="STSong-Light",
            fontSize=12,
            leading=18,
            textColor=colors.HexColor("#1c4738"),
            spaceBefore=6,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "BodyPdf",
            parent=base["Normal"],
            fontName="STSong-Light",
            fontSize=10.5,
            leading=17,
            textColor=colors.HexColor("#24322d"),
            spaceAfter=6,
        ),
        "table": ParagraphStyle(
            "TablePdf",
            parent=base["Normal"],
            fontName="STSong-Light",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#24322d"),
        ),
        "code": ParagraphStyle(
            "CodePdf",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor("#24322d"),
            backColor=colors.HexColor("#f4f7f5"),
            borderPadding=6,
        ),
    }
    return styles


def _build_pdf_story(markdown_text: str, solution_id: str, solution_name: str):
    styles = _build_pdf_styles()
    story = [
        Paragraph(_markdown_inline_to_reportlab(solution_name), styles["title"]),
        Paragraph(_markdown_inline_to_reportlab(f"Solution ID: {solution_id}"), styles["meta"]),
        Paragraph(_markdown_inline_to_reportlab(f"Exported At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), styles["meta"]),
        Spacer(1, 6 * mm),
    ]

    lines = markdown_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    list_type: Optional[str] = None
    table_lines: list[str] = []
    code_lines: list[str] = []
    in_code_block = False

    def flush_paragraph():
        nonlocal paragraph_lines
        if not paragraph_lines:
            return
        text = " ".join(part.strip() for part in paragraph_lines if part.strip())
        if text:
            story.append(Paragraph(_markdown_inline_to_reportlab(text), styles["body"]))
        paragraph_lines = []

    def flush_list():
        nonlocal list_items, list_type
        if not list_items:
            return
        bullet_type = "1" if list_type == "ordered" else "bullet"
        story.append(
            ListFlowable(
                [
                    ListItem(Paragraph(_markdown_inline_to_reportlab(item), styles["body"]))
                    for item in list_items
                ],
                bulletType=bullet_type,
                start="1",
                leftIndent=16,
            )
        )
        story.append(Spacer(1, 2 * mm))
        list_items = []
        list_type = None

    def flush_table():
        nonlocal table_lines
        if not table_lines:
            return

        rows = [_parse_markdown_table_row(line) for line in table_lines if line.strip()]
        if len(rows) < 2:
            for row in rows:
                if row:
                    story.append(Paragraph(_markdown_inline_to_reportlab(" | ".join(row)), styles["body"]))
            table_lines = []
            return

        if len(rows) >= 2 and _is_markdown_table_separator(table_lines[1]):
            header = rows[0]
            body_rows = rows[2:]
        else:
            header = rows[0]
            body_rows = rows[1:]

        normalized_rows = [header] + body_rows
        column_count = max(len(row) for row in normalized_rows)
        normalized_rows = [
            row + [""] * (column_count - len(row))
            for row in normalized_rows
        ]

        table_data = [
            [Paragraph(_markdown_inline_to_reportlab(cell), styles["table"]) for cell in row]
            for row in normalized_rows
        ]

        available_width = A4[0] - 28 * mm
        col_width = available_width / max(1, column_count)
        table = LongTable(table_data, repeatRows=1, colWidths=[col_width] * column_count)
        table.setStyle(
            TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef5f1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#123126")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d7e3dd")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(table)
        story.append(Spacer(1, 3 * mm))
        table_lines = []

    def flush_code():
        nonlocal code_lines
        if not code_lines:
            return
        story.append(Preformatted("\n".join(code_lines), styles["code"]))
        story.append(Spacer(1, 2 * mm))
        code_lines = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            flush_table()
            if in_code_block:
                flush_code()
            in_code_block = not in_code_block
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if stripped.startswith("|") and stripped.count("|") >= 2:
            flush_paragraph()
            flush_list()
            table_lines.append(stripped)
            continue

        if table_lines:
            flush_table()

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        heading_match = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            style_key = f"h{level}"
            story.append(Paragraph(_markdown_inline_to_reportlab(content), styles[style_key]))
            continue

        unordered_match = re.match(r"^[-*+]\s+(.*)$", stripped)
        ordered_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if unordered_match or ordered_match:
            flush_paragraph()
            current_type = "ordered" if ordered_match else "unordered"
            content = (ordered_match or unordered_match).group(1).strip()
            if list_type and list_type != current_type:
                flush_list()
            list_type = current_type
            list_items.append(content)
            continue

        if stripped in {"---", "***"}:
            flush_paragraph()
            flush_list()
            story.append(Spacer(1, 2 * mm))
            continue

        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    flush_table()
    flush_code()
    return story


def _generate_pdf_report(solution_id: str, solution_name: str, markdown_text: str) -> Path:
    output_dir = (PROJECT_ROOT / "src" / "greendatacenter" / "output" / "pdf_reports").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = _sanitize_export_filename(solution_name, f"solution_{solution_id}")
    pdf_path = output_dir / f"{safe_name}_{solution_id}.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=15 * mm,
        bottomMargin=14 * mm,
        title=solution_name,
        author="GreenDataCenter",
    )
    story = _build_pdf_story(markdown_text, solution_id, solution_name)
    doc.build(story)
    return pdf_path


async def _push_workflow_message(workflow_id: str, message: dict[str, Any]) -> None:
    queue = stream_queues.get(workflow_id)
    serializable = _make_serializable(message)
    if queue:
        await queue.put(serializable)
    if (
        "streaming_output" in workflows_store.get(workflow_id, {})
        and message.get("node") not in {"completed", "error", "heartbeat"}
    ):
        workflows_store[workflow_id]["streaming_output"].append(serializable)


async def _run_workflow(workflow_id: str, input_data: dict):
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

        parser = RequirementParserNode(coordinator.memory)
        normalized_requirement = parser._normalize_requirement(input_data)
        parsed_requirement = UserRequirement(**normalized_requirement)
        parsed_requirement_dict = parsed_requirement.model_dump()

        initial_state["user_requirement"] = parsed_requirement
        initial_state["requirement"] = parsed_requirement_dict

        await _push_workflow_message(
            workflow_id,
            {
                "node": "requirement_parser",
                "data": parsed_requirement_dict,
                "timestamp": datetime.now().isoformat(),
            },
        )

        accumulated_state = dict(initial_state)
        replayed_nodes = {"requirement_parser"}

        async for event in coordinator.compiled_graph.astream(initial_state):
            if not isinstance(event, dict):
                continue

            for node_name, node_output in event.items():
                if not isinstance(node_output, dict):
                    node_output = {"value": node_output}

                accumulated_state.update(node_output)

                if node_name == "requirement_parser":
                    continue

                payload = None
                inner_streaming_output = node_output.get("streaming_output")
                if isinstance(inner_streaming_output, list):
                    for entry in reversed(inner_streaming_output):
                        if isinstance(entry, dict) and entry.get("node") == node_name:
                            payload = entry.get("full_output")
                            break

                if payload is None:
                    payload = node_output

                await _push_workflow_message(
                    workflow_id,
                    {
                        "node": node_name,
                        "data": _make_serializable(payload),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                replayed_nodes.add(node_name)

        solution = _make_serializable(accumulated_state.get("solution", {}) or {})
        final_report = _make_serializable(accumulated_state.get("final_report_result", {}) or {})
        if isinstance(final_report, dict) and final_report:
            if not solution:
                solution = {}
            solution.update(final_report)

        if "output" not in replayed_nodes:
            await _push_workflow_message(
                workflow_id,
                {
                    "node": "output",
                    "data": {
                        "current_step": "completed",
                        "final_solution": solution,
                    },
                    "timestamp": datetime.now().isoformat(),
                },
            )

        streaming_output = _make_serializable(
            list(workflows_store.get(workflow_id, {}).get("streaming_output", []))
        )

        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        if solution:
            solution["generation_time"] = generation_time
            solution["created_at"] = end_time.isoformat()

        result = {
            "success": True,
            "solution": _make_serializable(solution),
            "streaming_output": streaming_output,
            "generation_time": generation_time,
        }

        solutions_store[workflow_id] = result
        workflows_store[workflow_id]["status"] = "completed"
        workflows_store[workflow_id]["result"] = result

        await _push_workflow_message(
            workflow_id,
            {
                "node": "completed",
                "data": _make_serializable(result),
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        traceback.print_exc()
        workflows_store[workflow_id]["status"] = "failed"
        workflows_store[workflow_id]["error"] = error_msg
        await _push_workflow_message(
            workflow_id,
            {
                "node": "error",
                "data": {"error": error_msg},
                "timestamp": datetime.now().isoformat(),
            },
        )
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
    final_report = _load_report_markdown_from_solution(sol)
    return {"content": final_report, "filename": f"report_{solution_id}.md"}


@app.get("/api/solutions/{solution_id}/export/pdf")
async def export_pdf(solution_id: str):
    if solution_id not in solutions_store:
        raise HTTPException(status_code=404, detail="Solution not found")

    sol = solutions_store[solution_id]
    final_report = _load_report_markdown_from_solution(sol).strip()
    if not final_report:
        raise HTTPException(status_code=404, detail="Report content not found")

    solution = sol.get("solution", {}) or {}
    solution_name = str(solution.get("name") or f"solution_{solution_id}")
    pdf_path = _generate_pdf_report(solution_id, solution_name, final_report)
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )


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
