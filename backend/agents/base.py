import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from beancount.core.data import Transaction
from fastapi import WebSocket
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.messages import BaseMessage

from accounting import store
from accounting.transactions import update_expense_categories


@dataclass
class TransactionForFeedback:
    transaction: Transaction
    assessed_category: str
    assessed_vendor: str
    rectified_category: str | None = None
    rectified_vendor: str | None = None

class Step(Enum):
    ORCHESTRATE = "orchestrate"
    CATEGORIZE = "categorize"
    GET_USER_FEEDBACK = "get_user_feedback"
    SUMMARIZE = "summarize"
    END = "end"

@dataclass
class AgentState:
    messages: Sequence[BaseMessage] = ()
    command: str = ""
    all_txns: list[Transaction] = field(default_factory=list)
    uncategorized_txns: list = field(default_factory=list)
    txns_to_update: list[dict] = field(default_factory=list)
    txns_to_get_feedback: list[TransactionForFeedback] = field(default_factory=list)
    next_step: Step = None
    websocket: WebSocket = None

    def refresh_transactions(self):
        self.all_txns = store.load()
        self.uncategorized_txns = [e for e in self.all_txns
                                           if isinstance(e, Transaction) and
                                           any(p.account.startswith('Expenses:Uncategorized') for p in e.postings)]
        self.txns_to_update = []
        print("Done refresh_transactions")
        print(self)

    async def flush_to_store(self):
        update_expense_categories(self.txns_to_update)
        self.refresh_transactions()
        print("Done flush_to_store")
        await self.websocket.send_json({
            "type": "STATE_UPDATE",
            "data": {
                "current_step": self.next_step.value,
                "progress": {
                    "total": len(self.all_txns),
                    "processed": len(self.all_txns) - len(self.uncategorized_txns),
                },
            }
        })
        await asyncio.sleep(2)
        print(self)


    def __str__(self):
        return (f"AgentState: next_step: {self.next_step} | all_txns: {len(self.all_txns)} | uncategorized_txns: {len(self.uncategorized_txns)} | "
                f"txns_to_update: {len(self.txns_to_update)} | "
                f"txns_to_get_feedback: {len(self.txns_to_get_feedback)}")


def get_llm():
    # return ChatAnthropic(model_name="claude-3-5-haiku-latest", timeout=300, temperature=0, stop=None)
    return ChatAnthropic(model_name="claude-3-haiku-20240307", timeout=300, temperature=0, stop=None)
