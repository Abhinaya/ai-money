from os import stat
from langchain_core.messages import AIMessage
import pandas as pd
from .base import AgentState, get_llm

from .categorizer import CATEGORIES
import streamlit as st

class OrchestratorAgent:
    def __init__(self):
        self.llm = get_llm()

    def route_command(self, state: AgentState) -> AgentState:
        """Routes the command to appropriate agent by updating state"""
        print("route_command", state["next_step"])
        if state["next_step"] != "orchestrator":
            return state
        command = state["command"].lower()
        if any(word in command for word in ["categorize", "classify", "label"]):
            # Set current_batch to all transactions if not specified
            if not state["current_batch"]:
                state["current_batch"] = state["transactions"]
            state["next_step"] = "categorizer"
            state["messages"].append(AIMessage(content="Routing to categorization agent"))

        elif any(word in command for word in ["summarize", "analyze", "show", "plot"]):
            state["next_step"] = "summarizer"
            state["messages"].append(AIMessage(content="Routing to summary agent"))

        else:
            state["next_step"] = "end"
            state["messages"].append(AIMessage(content="Unknown command, ending workflow"))

        return state

    def get_user_feedback_on_categorization(self, state: AgentState) -> AgentState:
        print("at get_user_feedback_on_categorization")
        with st.container():
            st.write("### Batch Categorization Results")
            txns_for_feedback = state['batch_for_feedback']
            summary_data = []
            for txn_for_feedback in txns_for_feedback:
                txn = txn_for_feedback.transaction
                summary_data.append({
                    'Date': txn.date,
                    'Vendor': txn.narration,
                    'Assessed Category': txn_for_feedback.assessed_category
                })
            edited_df = st.data_editor(
                pd.DataFrame(summary_data),
                column_config={
                    "Corrected Category": st.column_config.SelectboxColumn(
                        "Category",
                        options=CATEGORIES,
                        required=True
                    )
                }
            )
        state['next_step'] = 'end'
        print("at get_user_feedback_on_categorization end")
        return state
