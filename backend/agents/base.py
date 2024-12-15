from dataclasses import dataclass
from typing import TypedDict, Sequence
from beancount.core.data import Transaction
from langchain_anthropic.chat_models import ChatAnthropic
from langgraph.graph.state import Literal
from langchain_core.messages import BaseMessage


@dataclass
class TransactionForFeedback:
    transaction: Transaction
    assessed_category: str
    assessed_vendor: str
    rectified_category: str | None = None
    rectified_vendor: str | None = None


class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    command: str
    transactions: list
    current_batch: list[Transaction]
    batch_for_feedback: list[TransactionForFeedback]
    summary_data: dict
    plots: list
    next_step: Literal["orchestrator", "categorizer", "category_user_feedback", "summarizer", "end"]

def get_llm():
    # return ChatAnthropic(model_name="claude-3-5-haiku-latest", timeout=300, temperature=0, stop=None)
    return ChatAnthropic(model_name="claude-3-haiku-20240307", timeout=300, temperature=0, stop=None)
