from enum import Enum
from typing import Annotated, Literal
from langgraph.graph import StateGraph, Graph
from langgraph.graph.state import CompiledGraph
from agents.base import AgentState, Step
from agents.categorizer import CategorizationAgent
from agents.orchestrator import OrchestratorAgent
# from agents.summarizer import SummaryAgent


def log_transition(state: AgentState) -> AgentState:
    """Hook that logs state transitions"""
    print(f"State transition occurred. Current state: {state}")
    return state

def router(state: AgentState) -> str:
    """Router function that returns the next node based on state"""
    print("router state next_step: ", state.next_step)
    return state.next_step.value


def create_workflow() -> CompiledGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node(Step.ORCHESTRATE.value, OrchestratorAgent().orchestrate)
    workflow.add_node(Step.CATEGORIZE.value, CategorizationAgent().process_batch)
    workflow.add_node(Step.GET_USER_FEEDBACK.value, OrchestratorAgent().get_user_feedback)
    # workflow.add_node(Step.SUMMARIZE.value, SummaryAgent().create_summary)
    workflow.add_node(Step.END.value, lambda x: x)

    workflow.add_conditional_edges(Step.ORCHESTRATE.value, router, None, Step.ORCHESTRATE.value)

    workflow.set_entry_point(Step.ORCHESTRATE.value)
    return workflow.compile()
