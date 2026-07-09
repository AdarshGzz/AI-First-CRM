"""
WebSocket route: /ws/chat
Receives {message, current_state}, checks rate limit, invokes agent, streams response.
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.rate_limiter import check_rate_limit
from app.services.agent_service import invoke_agent

router = APIRouter()


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for the AI chat assistant.
    
    Protocol:
    - Client sends: {"message": "...", "current_state": {...}}
    - Server sends: {"type": "token", "content": "..."} (streaming)
    - Server sends: {"type": "result", "tool_used": "...", ...} (final)
    - Server sends: {"type": "rate_limited", "retry_after_seconds": N}
    - Server sends: {"type": "error", "message": "..."}
    """
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            raw_data = await websocket.receive_text()

            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format."
                })
                continue

            message = data.get("message", "").strip()
            current_state = data.get("current_state", {})

            if not message:
                await websocket.send_json({
                    "type": "error",
                    "message": "Message cannot be empty."
                })
                continue

            # ── Rate limit check ──────────────────────────
            try:
                allowed, retry_after = check_rate_limit()

                if not allowed:
                    await websocket.send_json({
                        "type": "rate_limited",
                        "retry_after_seconds": retry_after,
                    })
                    continue
            except Exception:
                # If Redis is down, log but don't block the request
                pass

            # ── Send "thinking" token ─────────────────────
            await websocket.send_json({
                "type": "token",
                "content": "🤔 Processing your message..."
            })

            # ── Invoke the LangGraph agent ────────────────
            result = await invoke_agent(message, current_state)

            # ── Send final result ─────────────────────────
            await websocket.send_json(result)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
        except Exception:
            pass
