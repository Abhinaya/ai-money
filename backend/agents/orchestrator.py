from accounting.catagory import CATEGORIES
from agents.base import AgentState, get_llm, Step


class OrchestratorAgent:
    def __init__(self):
        self.llm = get_llm()

    async def orchestrate(self, state: AgentState) -> AgentState:
        print(f"Orchestrate start {str(state)}")
        if not state.all_txns:
            state.refresh_transactions()
        if state.txns_to_get_feedback:
            state.next_step = Step.GET_USER_FEEDBACK
        elif state.uncategorized_txns:
            state.next_step = Step.CATEGORIZE
        else:
            await state.websocket.send_json({
                "type": "COMPLETE",
                "data": {
                    "progress": {
                        "total": len(state.all_txns),
                        "processed": len(state.all_txns) - len(state.uncategorized_txns),
                    },
                    "message": "Workflow completed successfully"
                }
            })
            state.next_step = Step.END
        print(f"Orchestrate next {str(state)}")
        return state

    async def get_user_feedback(self, state: AgentState) -> AgentState:
        print("GET USER FEEDBACK")
        await state.websocket.send_json({
            "type": "FEEDBACK_REQUIRED",
            "data": {
                "categories": [cat for cat in CATEGORIES if cat != "Expenses:Uncategorized"],
                "transactions": [{
                    "id": next(iter(txn.transaction.links)),
                    "date": str(txn.transaction.date),
                    "vendor": txn.transaction.narration,
                    "amount": str(txn.transaction.postings[0].units),
                    "assessed_category": txn.assessed_category,
                    "assessed_vendor": txn.assessed_vendor,
                    "rectified_category": txn.assessed_category,
                    "rectified_vendor": txn.assessed_vendor,
                } for txn in state.txns_to_get_feedback]
            }
        })
        feedback = await state.websocket.receive_json()
        if feedback["type"] == "SUBMIT_FEEDBACK":
            print(f"SUBMIT FEEDBACK: {feedback['data']}")
            state.txns_to_update.extend(feedback["data"]["transactions"])
        state.txns_to_get_feedback = []
        await state.flush_to_store()
        return state

