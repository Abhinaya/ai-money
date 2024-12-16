from agents.base import AgentState, get_llm, Step


class OrchestratorAgent:
    def __init__(self):
        self.llm = get_llm()

    def orchestrate(self, state: AgentState) -> AgentState:
        print(f"Orchestrate start {str(state)}")
        if not state.all_txns:
            state = AgentState()
            state.refresh_transactions()
        if state.txns_to_get_feedback:
            state.next_step = Step.GET_USER_FEEDBACK
        elif state.uncategorized_txns:
            state.next_step = Step.CATEGORIZE
        else:
            state.next_step = Step.END
        print(f"Orchestrate next {str(state)}")
        return state

    def get_user_feedback(self, state: AgentState) -> AgentState:
        print("GET USER FEEDBACK")
        state.uncategorized_txns = []
        return state

