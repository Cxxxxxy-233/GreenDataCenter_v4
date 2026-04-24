# -*- coding: utf-8 -*-
"""
图节点函数 - 修复版
"""

import io
import json
import sys
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel as PydanticBaseModel

from greendatacenter.llm.config import create_economic_llm, create_power_reliability_llm, create_environmental_llm, create_arbitrator_llm, create_requirement_parser_llm
from greendatacenter.memory import ExpertSharedMemory
from greendatacenter.graph.state import GraphState, ExpertOpinion, DebateMessage

# 强制UTF-8输出（仅在交互式控制台模式下）
# 这个会影响终端输出不要解开注释
# if sys.platform == "win32" and sys.stdout.isatty():
#     import io
#     sys.stdout = io.TextIOWrapper(sys.stdout, encoding="utf-8")
#     sys.stderr = io.TextIOWrapper(sys.stderr, encoding="utf-8")


class RequirementParserNode:
    """需求解析节点"""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a data center construction requirement parsing expert.

Your task is to analyze the user's data center construction requirements and extract key information, supplementing missing necessary parameters.

Analysis points:
1. Construction scale (rack count, server count)
2. Power requirements (total power, power density)
3. Reliability requirements (Tier level)
4. Cooling requirements (PUE target, cooling method)
5. Environmental requirements (green power ratio, carbon emission target)
6. Network requirements (bandwidth, redundancy)
7. Constraints (budget, site, schedule)
8. Project objectives and priorities

Output format requirements:
Output in JSON format with the following fields:
- name: requirement name
- rack_count: rack count (number)
- total_power: total power requirement (kW, number)
- power_density: power density (kW/rack, number)
- tier_level: reliability level (1-4)
- pue_target: PUE target value (number)
- green_power_ratio: green power ratio (0-1, number)
- budget: budget (wan yuan, number)
- floor_area: floor area (m2, number)
- bandwidth: bandwidth requirement (Gbps, number)
- objectives: objectives list
- constraints: constraints list
- priorities: priorities dictionary (economic/reliability/environmental)

If the user-provided information is incomplete, please supplement reasonable default values based on industry standards. Use Chinese for all field names and values."""),
            HumanMessage(content="User requirements: {requirement}\nPlease analyze and extract key information, output in JSON format. Use Chinese for all field names and values.")
        ])

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """执行需求解析"""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Requirement Parser] Start working...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        # 创建LLM并获取输出
        llm = create_requirement_parser_llm(on_chunk=self._on_stream_chunk)

        # 构建prompt
        requirement_text = json.dumps(state["requirement"], ensure_ascii=False, indent=2)

        messages = self.prompt_template.format_messages(requirement=requirement_text)

        # 调用LLM
        response = llm.invoke(messages)

        # 解析输出
        try:
            parsed_requirement = json.loads(response.content)
        except json.JSONDecodeError:
            # 如果JSON解析失败，使用原始需求
            parsed_requirement = state["requirement"]

        sys.stdout.write("[OK] Requirement parsing completed\n")
        sys.stdout.write(f"  - Rack count: {parsed_requirement.get('rack_count', 'N/A')}\n")
        sys.stdout.write(f"  - Total power: {parsed_requirement.get('total_power', 'N/A')} kW\n")
        sys.stdout.write(f"  - Tier level: {parsed_requirement.get('tier_level', 'N/A')}\n")
        sys.stdout.flush()

        # 记录流式输出
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "requirement_parser",
            "expert": "Requirement Parser",
            "content": f"Requirements parsed: {parsed_requirement.get('name', 'Unnamed')}",
            "full_output": parsed_requirement
        })

        return {
            "requirement": parsed_requirement,
            "current_step": "requirement_parsed",
            "streaming_output": streaming_output
        }

    def _on_stream_chunk(self, chunk: str):
        """流式输出回调"""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class EconomicAnalysisNode:
    """经济性分析专家节点"""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an economic analysis expert for data center construction solutions.

Your expertise:
- Data center construction cost estimation
- Return on Investment (ROI) analysis
- Cost-benefit evaluation
- Budget control recommendations

Analysis points:
1. Total cost estimation (equipment, construction, operations)
2. Cost per rack analysis
3. Return on Investment calculation
4. Payback period estimation
5. Budget compliance evaluation
6. Cost optimization recommendations

Scoring standards (0-1 points):
- cost_efficiency: cost efficiency
- roi: return on investment

Output format:
Output in JSON format with EXACTLY these field names (do NOT translate to Chinese):
```json
{{
  "expert_type": "economic",
  "expert_name": "Economic Analysis Expert-Zhang",
  "summary": "Opinion summary",
  "reasoning": "Detailed reasoning process",
  "scores": {{
    "cost_efficiency": 0.85,
    "roi": 0.12
  }},
  "metrics": {{
    "total_cost": 1800,
    "cost_per_rack": 18,
    "roi": 0.12,
    "payback_period": 8
  }},
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "concerns": ["Concern 1"],
  "confidence": 0.85
}}
```

IMPORTANT: Use EXACTLY the field names as shown above. Do not translate field names to Chinese. You can use Chinese for the values, but keep field names in English.

Please conduct professional analysis based on the requirements."""),
            HumanMessage(content="Data center construction requirements: {requirement}\nPlease conduct economic analysis. Use Chinese for all field names and values.")
        ])

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """执行经济性分析"""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Economic Analysis Expert] Start analysis...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        # 添加记忆上下文
        memory_context = self.memory.get_memory_context()
        requirement_text = json.dumps(state["requirement"], ensure_ascii=False, indent=2)

        # 创建LLM
        llm = create_economic_llm(on_chunk=self._on_stream_chunk)

        # 构建prompt
        base_prompt = self.prompt_template.format_messages(requirement=requirement_text)

        # 如果有记忆，添加到系统消息
        if memory_context:
            base_prompt.insert(
                -1,
                SystemMessage(content=f"[Previous discussion records]\n{memory_context}\n\nPlease refer to these discussion contents for your analysis. Use Chinese for all field names and values.")
            )

        # 调用LLM
        response = llm.invoke(base_prompt)

        # 解析输出
        opinion_data = self._parse_json_response(response.content)
        opinion = ExpertOpinion(**opinion_data)

        # 添加到记忆
        self.memory.add_expert_opinion(
            expert_name=opinion.expert_name,
            expert_type=opinion.expert_type,
            opinion=opinion.summary
        )

        sys.stdout.write("\n[OK] Economic analysis completed\n")
        sys.stdout.write(f"  - Estimated cost: {opinion.metrics.get('total_cost', 'N/A')} wan yuan\n")
        sys.stdout.write(f"  - ROI: {opinion.scores.get('roi', 'N/A')*100:.1f}%\n")
        sys.stdout.write(f"  - Cost efficiency: {opinion.scores.get('cost_efficiency', 'N/A'):.2f}\n")
        sys.stdout.flush()

        # 记录流式输出
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "economic_analysis",
            "expert": opinion.expert_name,
            "content": opinion.summary,
            "full_output": opinion.model_dump()
        })

        return {
            "economic_opinion": opinion,
            "streaming_output": streaming_output
        }

    def _parse_json_response(self, content: str) -> dict:
        """解析JSON响应 - 改进版"""
        import re

        # 首先尝试直接解析
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON块（处理markdown代码块）
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试直接查找JSON对象
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 尝试更复杂的JSON提取（处理嵌套结构）
        stack = []
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    try:
                        json_str = content[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

        # 如果所有尝试都失败，返回默认值
        sys.stderr.write(f"[WARN] Failed to parse JSON, using default values\n")
        return {
            "expert_type": "economic",
            "expert_name": "Economic Analysis Expert-Zhang",
            "summary": "Cost estimation completed",
            "reasoning": content[:500] if len(content) > 500 else content,
            "scores": {"cost_efficiency": 0.7, "roi": 0.1},
            "metrics": {},
            "recommendations": [],
            "concerns": [],
            "confidence": 0.6
        }

    def _on_stream_chunk(self, chunk: str):
        """流式输出回调"""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class PowerReliabilityAnalysisNode:
    """供电可靠性分析专家节点"""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a power reliability analysis expert for data center construction solutions.

Your expertise:
- Data center power system design
- UPS and redundancy configuration
- Tier standard compliance evaluation
- Power reliability analysis
- Risk assessment

Analysis points:
1. Determine power redundancy requirements based on Tier level
2. UPS capacity calculation and configuration
3. Power distribution architecture design (single bus/dual bus/redundant bus)
4. Expected availability calculation
5. Annual downtime estimation
6. Power risk assessment
7. Green power impact on reliability evaluation

Scoring standards (0-1 points):
- reliability: reliability score
- availability: availability score

Output format:
Output in JSON format with EXACTLY these field names (do NOT translate to Chinese):
```json
{{
  "expert_type": "power_reliability",
  "expert_name": "Power Reliability Expert-Li",
  "summary": "Opinion summary",
  "reasoning": "Detailed reasoning process",
  "scores": {{
    "reliability": 0.9,
    "availability": 0.9999
  }},
  "metrics": {{
    "tier_level": 3,
    "expected_availability": 99.98,
    "annual_downtime": 1.6,
    "ups_configuration": "2N UPS",
    "ups_capacity": 800,
    "distribution_reliability": 0.99
  }},
  "recommendations": ["Recommendation 1"],
  "concerns": ["Concern 1"],
  "confidence": 0.9
}}
```

IMPORTANT: Use EXACTLY the field names as shown above. Do not translate field names to Chinese. You can use Chinese for the values, but keep field names in English.

Please conduct professional analysis based on the requirements."""),
            HumanMessage(content="Data center construction requirements: {requirement}\nPlease conduct power reliability analysis.")
        ])

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """执行供电可靠性分析"""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Power Reliability Expert] Start analysis...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        # 添加记忆上下文
        memory_context = self.memory.get_memory_context()
        requirement_text = json.dumps(state["requirement"], ensure_ascii=False, indent=2)

        # 创建LLM
        llm = create_power_reliability_llm(on_chunk=self._on_stream_chunk)

        # 构建prompt
        base_prompt = self.prompt_template.format_messages(requirement=requirement_text)

        if memory_context:
            base_prompt.insert(
                -1,
                SystemMessage(content=f"[Previous discussion records]\n{memory_context}\n\nPlease refer to these discussion contents for your analysis. Use Chinese for all field names and values.")
            )

        # 调用LLM
        response = llm.invoke(base_prompt)

        # 解析输出
        opinion_data = self._parse_json_response(response.content)
        opinion = ExpertOpinion(**opinion_data)

        # 添加到记忆
        self.memory.add_expert_opinion(
            expert_name=opinion.expert_name,
            expert_type=opinion.expert_type,
            opinion=opinion.summary
        )

        sys.stdout.write("\n[OK] Power reliability analysis completed\n")
        sys.stdout.write(f"  - Expected availability: {opinion.metrics.get('expected_availability', 'N/A')}%\n")
        sys.stdout.write(f"  - Reliability score: {opinion.scores.get('reliability', 'N/A'):.2f}\n")
        sys.stdout.flush()

        # 记录流式输出
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "power_reliability_analysis",
            "expert": opinion.expert_name,
            "content": opinion.summary,
            "full_output": opinion.model_dump()
        })

        return {
            "power_reliability_opinion": opinion,
            "streaming_output": streaming_output
        }

    def _parse_json_response(self, content: str) -> dict:
        """解析JSON响应 - 改进版"""
        import re

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        stack = []
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    try:
                        json_str = content[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

        sys.stderr.write(f"[WARN] Failed to parse JSON, using default values\n")
        return {
            "expert_type": "power_reliability",
            "expert_name": "Power Reliability Expert-Li",
            "summary": "Reliability analysis completed",
            "reasoning": content[:500] if len(content) > 500 else content,
            "scores": {"reliability": 0.8, "availability": 0.999},
            "metrics": {},
            "recommendations": [],
            "concerns": [],
            "confidence": 0.7
        }

    def _on_stream_chunk(self, chunk: str):
        """流式输出回调"""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class EnvironmentalAnalysisNode:
    """环保性分析专家节点"""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an environmental analysis expert for data center construction solutions.

Your expertise:
- Carbon emission calculation and analysis
- PUE (Power Usage Effectiveness) evaluation
- Green power usage evaluation
- Environmental standard compliance
- Sustainable development recommendations

Analysis points:
1. PUE target evaluation (traditional >1.8, improved >1.5, efficient >1.3, ultra-efficient <=1.2)
2. Green power ratio evaluation (excellent >=80%, good >=60%, acceptable >=40%)
3. Annual carbon emission calculation
4. Cooling system environmental friendliness (refrigerant GWP value)
5. Carbon reduction potential analysis
6. Environmental optimization recommendations

Scoring standards (0-1 points):
- environmental_score: environmental score
- pue_score: PUE efficiency score
- green_power_score: green power usage score
- carbon_efficiency: carbon efficiency score

Output format:
Output in JSON format with EXACTLY these field names (do NOT translate to Chinese):
```json
{{
  "expert_type": "environmental",
  "expert_name": "Environmental Analysis Expert-Wang",
  "summary": "Opinion summary",
  "reasoning": "Detailed reasoning process",
  "scores": {{
    "environmental_score": 0.88,
    "pue_score": 0.95,
    "green_power_score": 0.9,
    "carbon_efficiency": 1.0
  }},
  "metrics": {{
    "pue_target": 1.3,
    "green_power_ratio": 0.7,
    "annual_carbon_emission": 250,
    "carbon_per_rack": 2.5
  }},
  "recommendations": ["Recommendation 1"],
  "concerns": ["Concern 1"],
  "confidence": 0.85
}}
```

IMPORTANT: Use EXACTLY the field names as shown above. Do not translate field names to Chinese. You can use Chinese for the values, but keep field names in English.

Please conduct professional analysis based on the requirements."""),
            HumanMessage(content="Data center construction requirements: {requirement}\nPlease conduct environmental analysis.")
        ])

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """执行环保性分析"""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Environmental Analysis Expert] Start analysis...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        # 添加记忆上下文
        memory_context = self.memory.get_memory_context()
        requirement_text = json.dumps(state["requirement"], ensure_ascii=False, indent=2)

        # 创建LLM
        llm = create_environmental_llm(on_chunk=self._on_stream_chunk)

        # 构建prompt
        base_prompt = self.prompt_template.format_messages(requirement=requirement_text)

        if memory_context:
            base_prompt.insert(
                -1,
                SystemMessage(content=f"[Previous discussion records]\n{memory_context}\n\nPlease refer to these discussion contents for your analysis. Use Chinese for all field names and values.")
            )

        # 调用LLM
        response = llm.invoke(base_prompt)

        # 解析输出
        opinion_data = self._parse_json_response(response.content)
        opinion = ExpertOpinion(**opinion_data)

        # 添加到记忆
        self.memory.add_expert_opinion(
            expert_name=opinion.expert_name,
            expert_type=opinion.expert_type,
            opinion=opinion.summary
        )

        sys.stdout.write("\n[OK] Environmental analysis completed\n")
        sys.stdout.write(f"  - Annual carbon emission: {opinion.metrics.get('annual_carbon_emission', 'N/A')} tons\n")
        sys.stdout.write(f"  - Environmental score: {opinion.scores.get('environmental_score', 'N/A'):.2f}\n")
        sys.stdout.flush()

        # 记录流式输出
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "environmental_analysis",
            "expert": opinion.expert_name,
            "content": opinion.summary,
            "full_output": opinion.model_dump()
        })

        return {
            "environmental_opinion": opinion,
            "streaming_output": streaming_output
        }

    def _parse_json_response(self, content: str) -> dict:
        """解析JSON响应 - 改进版"""
        import re

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        stack = []
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    try:
                        json_str = content[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

        sys.stderr.write(f"[WARN] Failed to parse JSON, using default values\n")
        return {
            "expert_type": "environmental",
            "expert_name": "Environmental Analysis Expert-Wang",
            "summary": "Environmental analysis completed",
            "reasoning": content[:500] if len(content) > 500 else content,
            "scores": {"environmental_score": 0.8, "pue_score": 0.8, "green_power_score": 0.8, "carbon_efficiency": 0.8},
            "metrics": {},
            "recommendations": [],
            "concerns": [],
            "confidence": 0.7
        }

    def _on_stream_chunk(self, chunk: str):
        """流式输出回调"""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class DebateRoundNode:
    """辩论轮次节点"""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """执行一轮辩论"""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write(f"[Debate Round {state['debate_round']}] Start...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        # 获取专家意见
        economic_opinion = state.get("economic_opinion")
        power_opinion = state.get("power_reliability_opinion")
        environmental_opinion = state.get("environmental_opinion")

        if not all([economic_opinion, power_opinion, environmental_opinion]):
            sys.stdout.write("[SKIP] Expert opinions incomplete, skip debate\n")
            return {
                "should_continue_debate": False,
                "consensus_reached": True
            }

        # 组织轮流发言
        streaming_output = state.get("streaming_output", [])

        # 第1位发言：经济性专家
        self._expert_speak(
            speaker=economic_opinion.expert_name,
            state=state,
            streaming_output=streaming_output,
            current_opinion=economic_opinion,
            other_opinions=[power_opinion, environmental_opinion]
        )

        # 第2位发言：供电可靠性专家
        self._expert_speak(
            speaker=power_opinion.expert_name,
            state=state,
            streaming_output=streaming_output,
            current_opinion=power_opinion,
            other_opinions=[economic_opinion, environmental_opinion]
        )

        # 第3位发言：环保性专家
        self._expert_speak(
            speaker=environmental_opinion.expert_name,
            state=state,
            streaming_output=streaming_output,
            current_opinion=environmental_opinion,
            other_opinions=[economic_opinion, power_opinion]
        )

        # 评估共识度
        consensus_score = self._evaluate_consensus(state)

        sys.stdout.write(f"\n[OK] Debate round {state['debate_round']} completed\n")
        sys.stdout.write(f"  - Consensus score: {consensus_score:.2f}\n")
        sys.stdout.flush()

        return {
            "debate_round": state["debate_round"] + 1,
            "consensus_score": consensus_score,
            "should_continue_debate": consensus_score < 0.8,
            "consensus_reached": consensus_score >= 0.8,
            "streaming_output": streaming_output
        }

    def _expert_speak(
        self,
        speaker: str,
        state: GraphState,
        streaming_output: list,
        current_opinion: ExpertOpinion,
        other_opinions: list[ExpertOpinion]
    ):
        """专家发言"""
        sys.stdout.write(f"\n[{speaker} speaking...]\n")
        sys.stdout.flush()

        # 构建prompt
        other_opinions_text = "\n".join([
            f"- {op.expert_name}: {op.summary}"
            for op in other_opinions
        ])

        prompt = f"""You are {speaker}, a data center construction solution design expert.

Your main point:
{current_opinion.summary}

Reasoning:
{current_opinion.reasoning}

Other experts' points:
{other_opinions_text}

[Debate task]
Now please express your opinion, focusing on:
1. Respond to other experts' points
2. State what you agree or disagree with reasons
3. Propose possible coordination solutions
4. Reveal trade-offs between different dimensions

Please respond concisely in Chinese, within 200 characters."""

        # 创建LLM
        from greendatacenter.llm.config import get_llm
        llm = get_llm(
            temperature=0.6,
            max_tokens=300,
            on_chunk=self._on_stream_chunk,
            timeout=30
        )

        # 调用LLM
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content="You are a data center construction solution design debate expert."),
            HumanMessage(content=prompt)
        ]

        response = llm.invoke(messages)
        opinion = response.content.strip()

        sys.stdout.write(f"{speaker}: {opinion}\n")
        sys.stdout.flush()

        # 添加到记忆
        self.memory.add_debate_message(
            speaker=speaker,
            listener=None,
            message=opinion,
            message_type="statement"
        )

        # 记录流式输出
        streaming_output.append({
            "node": "debate",
            "expert": speaker,
            "content": opinion,
            "round": state["debate_round"]
        })

    def _evaluate_consensus(self, state: GraphState) -> float:
        """评估共识度"""
        # 简化版：基于专家评分的方差计算共识度
        economic_score = state.get("economic_opinion")
        power_score = state.get("power_reliability_opinion")
        environmental_score = state.get("environmental_opinion")

        if not all([economic_score, power_score, environmental_score]):
            return 0.5

        # 提取主要评分
        econ_main = self._extract_main_score(economic_score.scores)
        power_main = self._extract_main_score(power_score.scores)
        env_main = self._extract_main_score(environmental_score.scores)

        scores = [econ_main, power_main, env_main]
        mean_score = sum(scores) / len(scores)

        # 计算标准差作为分歧度
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        divergence = variance ** 0.5

        # 共识度 = 1 - 分歧度
        consensus = max(0, min(1, 1 - divergence))

        return consensus

    def _extract_main_score(self, scores: dict) -> float:
        """提取主要评分"""
        if not scores:
            return 0.5

        # 获取第一个数值评分
        for value in scores.values():
            if isinstance(value, (int, float)):
                return value

        return 0.5

    def _on_stream_chunk(self, chunk: str):
        """流式输出回调"""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class ArbitratorNode:
    """仲裁决策节点"""

    def __init__(self, memory: ExpertSharedMemory):
        self.memory = memory

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """执行仲裁决策"""
        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Arbitrator] Start comprehensive analysis...\n")
        sys.stdout.write("="*60 + "\n")
        sys.stdout.flush()

        # 获取所有专家意见
        economic_opinion = state.get("economic_opinion")
        power_opinion = state.get("power_reliability_opinion")
        environmental_opinion = state.get("environmental_opinion")
        debate_round = state.get("debate_round", 0)

        # 构建仲裁prompt
        opinions_text = f"""
[Economic Analysis Expert-{economic_opinion.expert_name}]
Summary: {economic_opinion.summary}
Reasoning: {economic_opinion.reasoning}
Scores: {economic_opinion.scores}
Key metrics: {economic_opinion.metrics}
Recommendations: {economic_opinion.recommendations}

[Power Reliability Expert-{power_opinion.expert_name}]
Summary: {power_opinion.summary}
Reasoning: {power_opinion.reasoning}
Scores: {power_opinion.scores}
Key metrics: {power_opinion.metrics}
Recommendations: {power_opinion.recommendations}

[Environmental Analysis Expert-{environmental_opinion.expert_name}]
Summary: {environmental_opinion.summary}
Reasoning: {environmental_opinion.reasoning}
Scores: {environmental_opinion.scores}
Key metrics: {environmental_opinion.metrics}
Recommendations: {environmental_opinion.recommendations}

[Debate status]
Completed {debate_round} rounds of debate
"""

        prompt = f"""You are a data center construction solution arbitrator.

Your task is to synthesize opinions from economic, power reliability, and environmental analysis experts to generate the final construction solution.

{opinions_text}

[Arbitration task]
1. Analyze consistency and disagreements among expert opinions
2. Balance conflicts between different dimensions
3. Generate optimal solution that accommodates multi-party requirements
4. Clarify final solution's overall scores and key metrics

Output format requirements (JSON) with EXACTLY these field names (do NOT translate to Chinese):
```json
{{
  "name": "Solution name",
  "summary": "Solution summary",
  "overall_scores": {{
    "economic": 0.85,
    "reliability": 0.9,
    "environmental": 0.88,
    "overall": 0.88
  }},
  "key_metrics": {{
    "total_cost": 1800,
    "pue": 1.3,
    "green_power_ratio": 0.7,
    "tier_level": 3,
    "expected_availability": 99.98,
    "annual_carbon_emission": 250
  }},
  "economic_section": {{
    "description": "Economic solution description",
    "content": {{"total_cost": 1800, "roi": 0.12}},
    "recommendations": ["Recommendation 1"]
  }},
  "power_reliability_section": {{
    "description": "Power reliability solution description",
    "content": {{"tier_level": 3, "ups_configuration": "2N"}},
    "recommendations": ["Recommendation 1"]
  }},
  "environmental_section": {{
    "description": "Environmental solution description",
    "content": {{"pue": 1.3, "green_power_ratio": 0.7}},
    "recommendations": ["Recommendation 1"]
  }},
  "trade_offs": [
    {{"conflict": "Cost vs Reliability", "resolution": "Prioritize reliability with optimization"}}
  ],
  "risks": [
    {{"type": "Power supply", "description": "Risk description"}}
  ],
  "recommendations": [
    "Final recommendation 1",
    "Final recommendation 2"
  ],
  "confidence": 0.85
}}
```

IMPORTANT: Use EXACTLY the field names as shown above. Do not translate field names to Chinese. You can use Chinese for the values, but keep field names in English.

Please conduct arbitration decision and generate final solution."""

        # 创建LLM
        llm = create_arbitrator_llm(on_chunk=self._on_stream_chunk)

        # 调用LLM
        from langchain_core.messages import HumanMessage, SystemMessage
        messages = [
            SystemMessage(content="You are a data center construction solution design arbitrator."),
            HumanMessage(content=prompt)
        ]

        response = llm.invoke(messages)

        # 解析输出
        solution_data = self._parse_json_response(response.content)

        sys.stdout.write("\n[OK] Arbitration decision completed\n")
        sys.stdout.write(f"  - Overall score: {solution_data.get('overall_scores', {}).get('overall', 0):.2f}\n")
        sys.stdout.write(f"  - Confidence: {solution_data.get('confidence', 0.8):.2f}\n")
        sys.stdout.flush()

        # 记录流式输出
        streaming_output = state.get("streaming_output", [])
        streaming_output.append({
            "node": "arbitrator",
            "expert": "Arbitrator",
            "content": "Generated final construction solution",
            "full_output": solution_data
        })

        return {
            "solution": solution_data,
            "streaming_output": streaming_output
        }

    def _parse_json_response(self, content: str) -> dict:
        """解析JSON响应 - 改进版"""
        import re

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        stack = []
        start_idx = None
        for i, char in enumerate(content):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    try:
                        json_str = content[start_idx:i+1]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

        sys.stderr.write(f"[WARN] Failed to parse JSON, using default values\n")
        return {
            "name": "Construction Solution",
            "summary": "Synthesized expert opinions to generate solution",
            "overall_scores": {"overall": 0.75},
            "key_metrics": {},
            "economic_section": {},
            "power_reliability_section": {},
            "environmental_section": {},
            "trade_offs": [],
            "risks": [],
            "recommendations": [],
            "confidence": 0.6
        }

    def _on_stream_chunk(self, chunk: str):
        """流式输出回调"""
        sys.stdout.write(chunk)
        sys.stdout.flush()


class OutputNode:
    """输出节点"""

    def __call__(self, state: GraphState) -> dict[str, Any]:
        """执行输出"""
        solution = state.get("solution", {})
        streaming_output = state.get("streaming_output", [])

        sys.stdout.write("\n" + "="*60 + "\n")
        sys.stdout.write("[Final Solution]\n")
        sys.stdout.write("="*60 + "\n")

        sys.stdout.write(f"\nSolution name: {solution.get('name', 'Unnamed')}\n")
        sys.stdout.write(f"Solution summary: {solution.get('summary', '')}\n")
        sys.stdout.write(f"\nOverall score: {solution.get('overall_scores', {}).get('overall', 0):.2f}\n")
        sys.stdout.flush()

        return {
            "current_step": "completed",
            "final_solution": solution,
            "streaming_output": streaming_output
        }
