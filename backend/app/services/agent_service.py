"""
Agent service — the bridge between the WebSocket router and LangGraph.
Invokes the compiled graph, formats the response into the standard API contract.
"""

from langchain_core.messages import HumanMessage
from app.agents.graph import agent_graph
from app.models.schemas import WSResultMessage


async def invoke_agent(message: str, current_state: dict) -> dict:
    """
    Run the LangGraph agent with the user's message and current form state.
    
    Returns a dict matching the WSResultMessage schema:
    {
        "type": "result",
        "tool_used": "...",
        "updated_state": {...},
        "chat_reply": "...",
        "suggested_followups": [...]
    }
    """
    # Build the initial state for the graph
    initial_state = {
        "messages": [HumanMessage(content=message)],
        "current_form_state": current_state or {},
        "intent": "",
        "tool_output": {},
    }

    try:
        # Invoke the compiled graph
        result = await agent_graph.ainvoke(initial_state)

        # Extract the tool output
        tool_output = result.get("tool_output", {})

        return {
            "type": "result",
            "tool_used": tool_output.get("tool_used", "unknown"),
            "updated_state": tool_output.get("updated_state", {}),
            "chat_reply": tool_output.get("chat_reply", "I processed your request."),
            "suggested_followups": tool_output.get("suggested_followups", []),
        }

    except Exception as e:
        return {
            "type": "error",
            "message": f"Agent error: {str(e)}",
            "tool_used": "error",
            "updated_state": {},
            "chat_reply": f"❌ Something went wrong: {str(e)}. Please try again.",
            "suggested_followups": [],
        }
