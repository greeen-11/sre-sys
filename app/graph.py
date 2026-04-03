
from langgraph.graph import StateGraph, END

from app.state import AgentState
from app.nodes import (
    start_run, run_validation, analyze_failure,
    gather_context, generate_patch, apply_patch,
    summarize_result, abort
)

def route_after_validation(state: AgentState) -> str:
    if state["last_exit_code"] == 0:
        return "summarize_result"
    if state["attempt_count"] >= state["max_retries"]:
        return "abort"
    return "analyze_failure"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("start_run", start_run)
    graph.add_node("run_validation", run_validation)
    graph.add_node("analyze_failure", analyze_failure)
    graph.add_node("gather_context", gather_context)
    graph.add_node("generate_patch", generate_patch)
    graph.add_node("apply_patch", apply_patch)
    graph.add_node("summarize_result", summarize_result)
    graph.add_node("abort", abort)

    graph.set_entry_point("start_run")

    graph.add_edge("start_run", "run_validation")
    graph.add_edge("analyze_failure", "gather_context")
    graph.add_edge("gather_context", "generate_patch")
    graph.add_edge("generate_patch", "apply_patch")
    graph.add_edge("apply_patch", "run_validation")

    graph.add_conditional_edges("run_validation", route_after_validation)

    graph.add_edge("summarize_result", END)
    graph.add_edge("abort", END)

    return graph.compile()

