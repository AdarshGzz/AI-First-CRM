"""
LangGraph agent state schema.
This TypedDict is shared across all nodes in the graph.
"""

from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State carried through the LangGraph execution graph."""

    # Chat history — accumulated via LangGraph's add_messages reducer
    messages: Annotated[list[BaseMessage], add_messages]

    # Current Redux form state sent from the frontend
    current_form_state: dict

    # Router-classified intent: which tool to invoke
    intent: str

    # The validated tool output payload to return to the frontend
    tool_output: dict
