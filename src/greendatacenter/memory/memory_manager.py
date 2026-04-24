"""
记忆管理模块
简化版实现
"""

from typing import Any, Optional


class ExpertSharedMemory:
    """专家共享记忆（简化版）"""

    def __init__(self, llm: Optional[Any] = None):
        """
        初始化专家共享记忆

        Args:
            llm: 用于生成摘要的LLM（暂不使用）
        """
        self.llm = llm

        # 存储完整的对话历史
        self.chat_history: list[dict] = []

        # 存储摘要
        self.summary: str = ""

    @property
    def memory_variables(self) -> list[str]:
        """记忆变量"""
        return ["history", "summary"]

    def load_memory_variables(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """加载记忆变量"""
        history = self._format_history()
        return {
            "history": history,
            "summary": self.summary
        }

    def save_context(self, inputs: dict[str, Any], outputs: dict[str, str]) -> None:
        """
        保存上下文到记忆

        Args:
            inputs: 输入
            outputs: 输出
        """
        # 添加专家发言到历史
        if "expert" in inputs and "opinion" in outputs:
            expert_name = inputs["expert"]
            opinion = outputs.get("opinion", "")

            self.chat_history.append({
                "role": "assistant",
                "name": expert_name,
                "content": opinion
            })

        # 如果对话太长，生成摘要
        if len(self.chat_history) > 10:
            self._summarize_history()

    def _summarize_history(self) -> None:
        """生成对话摘要"""
        if not self.chat_history:
            return

        # 简化版：直接取最近几条作为摘要
        recent_messages = self.chat_history[-5:]
        self.summary = self._format_messages(recent_messages)

        # 清空历史，保留摘要
        self.chat_history = []

    def _format_history(self) -> str:
        """格式化历史记录"""
        if not self.chat_history:
            return ""

        formatted = []
        for msg in self.chat_history:
            expert = msg.get("name", "专家")
            content = msg.get("content", "")
            formatted.append(f"{expert}: {content}")
        return "\n\n".join(formatted)

    def _format_messages(self, messages: list[dict]) -> str:
        """格式化消息列表"""
        formatted = []
        for msg in messages:
            expert = msg.get("name", "专家")
            content = msg.get("content", "")
            formatted.append(f"{expert}: {content}")
        return "\n\n".join(formatted)

    def clear(self) -> None:
        """清空记忆"""
        self.chat_history = []
        self.summary = ""

    def add_expert_opinion(
        self,
        expert_name: str,
        expert_type: str,
        opinion: str
    ) -> None:
        """
        添加专家意见到记忆

        Args:
            expert_name: 专家名称
            expert_type: 专家类型
            opinion: 专家意见
        """
        self.chat_history.append({
            "role": "assistant",
            "name": f"{expert_name}({expert_type})",
            "content": opinion
        })

    def add_debate_message(
        self,
        speaker: str,
        listener: Optional[str],
        message: str,
        message_type: str
    ) -> None:
        """
        添加辩论消息到记忆

        Args:
            speaker: 发言者
            listener: 倾听者（None表示广播）
            message: 消息内容
            message_type: 消息类型
        """
        if listener:
            content = f"{speaker}对{listener}说：{message} ({message_type})"
        else:
            content = f"{speaker}发言：{message} ({message_type})"

        self.chat_history.append({
            "role": "assistant",
            "name": speaker,
            "content": content
        })

    def get_memory_context(self) -> str:
        """
        获取记忆上下文用于prompt

        Returns:
            记忆上下文字符串
        """
        context_parts = []

        if self.summary:
            context_parts.append(f"【历史摘要】\n{self.summary}")

        if self.chat_history:
            recent_history = self.chat_history[-5:]  # 最近5条
            history_text = "\n".join([
                f"{msg.get('name', '专家')}: {msg.get('content', '')}"
                for msg in recent_history
            ])
            context_parts.append(f"【最近讨论】\n{history_text}")

        return "\n\n".join(context_parts)
