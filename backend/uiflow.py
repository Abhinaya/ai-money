from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agents.base import AgentState
from agents.workflow import create_workflow

router   = APIRouter()

@router.websocket("/ws/workflow")
async def workflow_socket(websocket: WebSocket, beancount_filepath: str):
    await websocket.accept()
    try:
        state = AgentState(websocket=websocket, beancount_filepath=beancount_filepath)
        wf = create_workflow()
        await wf.ainvoke(state, {"recursion_limit": 100})
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"type": "ERROR", "message": str(e)})
        raise Exception(e)
    finally:
        await websocket.close()
