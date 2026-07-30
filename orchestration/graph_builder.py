"""Build the LangGraph workflow that coordinates the BuildSense agents."""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from orchestration.hitl_node import human_review_node
from orchestration.nodes import (
    analyze_node,
    cancel_node,
    collect_node,
    controller_node,
    retry_collection_node,
    strategy_node,
)
from orchestration.state import BuildSenseState


WorkerRoute = Literal[
    "collect",
    "retry_collection",
    "analyze",
    "strategy",
    "human_review",
    "cancel",
]


def route_controller(state: BuildSenseState) -> WorkerRoute:
    """Route the graph to the single worker selected by the controller node."""
    action = state.get("next_action")
    allowed = {
        "collect",
        "retry_collection",
        "analyze",
        "strategy",
        "human_review",
        "cancel",
    }
    if action not in allowed:
        raise RuntimeError(f"Controller selected unknown action: {action}")
    return action


def build_graph():
    """Compile and return the real LangGraph StateGraph runtime."""
    builder = StateGraph(BuildSenseState)

    # The controller reasons about the current state; worker nodes perform one
    # action and return their observation to the controller.
    builder.add_node("controller", controller_node)
    builder.add_node("collect", collect_node)
    builder.add_node("retry_collection", retry_collection_node)
    builder.add_node("analyze", analyze_node)
    builder.add_node("strategy", strategy_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("cancel", cancel_node)

    builder.add_edge(START, "controller")
    builder.add_conditional_edges(
        "controller",
        route_controller,
        {
            "collect": "collect",
            "retry_collection": "retry_collection",
            "analyze": "analyze",
            "strategy": "strategy",
            "human_review": "human_review",
            "cancel": "cancel",
        },
    )

    # Every non-terminal worker returns to the controller so the next step is
    # chosen from fresh observations instead of following a fixed pipeline.
    for worker in ("collect", "retry_collection", "analyze", "strategy"):
        builder.add_edge(worker, "controller")

    builder.add_edge("human_review", END)
    builder.add_edge("cancel", END)
    return builder.compile()
