"""
LLM配置模块
"""

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.callbacks import BaseCallbackHandler

load_dotenv()


class StreamingCallbackHandler(BaseCallbackHandler):
    """流式输出回调处理器"""

    def __init__(self, on_chunk: callable):
        """
        初始化回调处理器

        Args:
            on_chunk: 当收到新token时的回调函数
        """
        self.on_chunk = on_chunk

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """当LLM生成新token时调用"""
        self.on_chunk(token)


def get_llm(
    model: str = "deepseek-chat",
    api_key: Optional[str] = None,
    base_url: str = "https://api.deepseek.com",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    streaming: bool = True,
    on_chunk: Optional[callable] = None,
    timeout: int = 60
) -> BaseChatModel:
    """
    获取LLM实例

    Args:
        model: 模型名称
        api_key: API密钥
        base_url: API基础URL
        temperature: 温度参数
        max_tokens: 最大token数
        streaming: 是否启用流式输出
        on_chunk: 流式输出回调函数
        timeout: 超时时间(秒)

    Returns:
        LLM实例
    """
    if api_key is None:
        api_key = os.getenv("LLM_API_KEY", "")
        if not api_key:
            raise RuntimeError("缺少环境变量 LLM_API_KEY")

    # 创建回调列表
    callbacks = []
    if streaming and on_chunk:
        callbacks.append(StreamingCallbackHandler(on_chunk))

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming,
        callbacks=callbacks,
        timeout=timeout,
    )

    return llm


def create_economic_llm(on_chunk: Optional[callable] = None) -> BaseChatModel:
    """创建经济性分析专家使用的LLM"""
    return get_llm(
        temperature=0.5,
        max_tokens=1500,
        on_chunk=on_chunk,
        timeout=60
    )


def create_power_reliability_llm(on_chunk: Optional[callable] = None) -> BaseChatModel:
    """创建供电可靠性专家使用的LLM"""
    return get_llm(
        temperature=0.3,
        max_tokens=1500,
        on_chunk=on_chunk,
        timeout=60
    )


def create_environmental_llm(on_chunk: Optional[callable] = None) -> BaseChatModel:
    """创建环保性分析专家使用的LLM"""
    return get_llm(
        temperature=0.4,
        max_tokens=1500,
        on_chunk=on_chunk,
        timeout=60
    )


def create_arbitrator_llm(on_chunk: Optional[callable] = None) -> BaseChatModel:
    """创建仲裁决策使用的LLM"""
    return get_llm(
        temperature=0.5,
        max_tokens=2500,
        on_chunk=on_chunk,
        timeout=90
    )


def create_requirement_parser_llm(on_chunk: Optional[callable] = None) -> BaseChatModel:
    """创建需求解析使用的LLM"""
    return get_llm(
        temperature=0.3,
        max_tokens=1000,
        on_chunk=on_chunk,
        timeout=60
    )
