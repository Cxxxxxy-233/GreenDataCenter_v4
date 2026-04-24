"""
辩论数据模型
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DebateStatus(str, Enum):
    """辩论状态"""
    PENDING = "pending"  # 待开始
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    ABORTED = "aborted"  # 已中止


class DebateMessageType(str, Enum):
    """辩论消息类型"""
    OPINION = "opinion"  # 陈述意见
    CHALLENGE = "challenge"  # 挑战
    SUPPORT = "support"  # 支持
    QUESTION = "question"  # 提问
    ANSWER = "answer"  # 回答
    CONCLUSION = "conclusion"  # 结论


class DebateMessage(BaseModel):
    """辩论消息"""

    id: str = Field(default="", description="消息ID")
    round_id: str = Field(..., description="所属辩论轮次ID")
    sender: str = Field(..., description="发送者ID")
    receiver: Optional[str] = Field(None, description="接收者ID (None表示广播)")
    message_type: DebateMessageType = Field(..., description="消息类型")
    content: str = Field(..., description="消息内容")
    evidence: list[str] = Field(default_factory=list, description="支撑证据")

    # 元数据
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

    def model_post_init(self, __context):
        """模型初始化后处理"""
        if not self.id:
            self.id = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"


class DebateRound(BaseModel):
    """辩论轮次"""

    id: str = Field(default="", description="轮次ID")
    requirement_id: str = Field(..., description="关联的需求ID")
    status: DebateStatus = Field(default=DebateStatus.PENDING, description="辩论状态")
    round_number: int = Field(..., description="轮次编号")

    # 辩论内容
    messages: list[DebateMessage] = Field(default_factory=list, description="辩论消息列表")

    # 辩论结果
    conflicts_identified: list[dict] = Field(default_factory=list, description="识别的冲突点")
    consensus_points: list[str] = Field(default_factory=list, description="达成共识的点")
    open_issues: list[str] = Field(default_factory=list, description="待解决问题")

    # 元数据
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    def model_post_init(self, __context):
        """模型初始化后处理"""
        if not self.id:
            self.id = f"round_{self.round_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def add_message(self, message: DebateMessage):
        """添加辩论消息"""
        self.messages.append(message)

    def mark_started(self):
        """标记辩论开始"""
        self.status = DebateStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def mark_completed(self):
        """标记辩论完成"""
        self.status = DebateStatus.COMPLETED
        self.completed_at = datetime.now()


class DebateSession(BaseModel):
    """辩论会话"""

    id: str = Field(default="", description="会话ID")
    requirement_id: str = Field(..., description="关联的需求ID")
    status: DebateStatus = Field(default=DebateStatus.PENDING, description="会话状态")

    # 辩论轮次
    rounds: list[DebateRound] = Field(default_factory=list, description="辩论轮次列表")
    max_rounds: int = Field(default=3, description="最大辩论轮次")

    # 专家参与者
    participants: list[str] = Field(default_factory=list, description="参与专家ID列表")

    # 最终结论
    final_conclusion: Optional[str] = Field(None, description="最终结论")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    def model_post_init(self, __context):
        """模型初始化后处理"""
        if not self.id:
            self.id = f"debate_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def add_round(self, round: DebateRound):
        """添加辩论轮次"""
        self.rounds.append(round)

    def start_next_round(self) -> Optional[DebateRound]:
        """开始下一轮辩论"""
        if len(self.rounds) >= self.max_rounds:
            return None

        next_round = DebateRound(
            requirement_id=self.requirement_id,
            round_number=len(self.rounds) + 1
        )
        next_round.mark_started()
        self.add_round(next_round)
        self.status = DebateStatus.IN_PROGRESS
        return next_round
