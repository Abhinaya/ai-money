from agents.base import AgentState
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import asyncio
from session import SessionStore
from accounting import store
from beancount.core import data
from accounting.transactions import update_expense_categories
from agents.categorizer import CATEGORIES, BATCH_SIZE, CategorizationAgent

router = APIRouter()
session_store = SessionStore()

def uncategorized_transactions(transactions):
    if transactions is None:
        transactions = store.load()
    return [e for e in transactions
            if isinstance(e, data.Transaction) and
            any(p.account.startswith('Expenses:Uncategorized') for p in e.postings)]

@router.websocket("/ws/workflow")
async def workflow_socket(websocket: WebSocket):
    await websocket.accept()

    try:
        all_transactions = store.load()
        uncategorized_txns = uncategorized_transactions(all_transactions)
        session_id = session_store.create_session()
        batch_size = len(uncategorized_txns) if len(uncategorized_txns) < BATCH_SIZE else BATCH_SIZE

        state = AgentState(
            messages=[],
            command="",
            transactions=uncategorized_txns,
            current_batch=uncategorized_txns[:batch_size],
            batch_for_feedback=[],
            summary_data={},
            plots=[],
            next_step="categorizer"
        )

        session_store.update_session(session_id, state)

        # Notify frontend of session initialization
        await websocket.send_json(
            {
            "type": "SESSION_INITIALIZED",
            "data": {
                "session_id": session_id,
                "progress": {
                    "total": len(all_transactions),
                    "processed": len(all_transactions) - len(uncategorized_txns),
                }
            }
        })

        while True:
            # Fetch the latest session state
            state = session_store.get_session(session_id)
            if not state:
                raise HTTPException(status_code=404, detail="Session not found")

            # Process categorization
            if state["next_step"] == "categorizer":
                categorizer = CategorizationAgent()
                updated_state = categorizer.process_batch(state)
                session_store.update_session(session_id, updated_state)

                if updated_state["next_step"] == "end":
                    continue
                # Send updated batch to frontend for feedback
                if not updated_state["batch_for_feedback"]:
                    print("nothing for feedback")
                    await websocket.send_json({
                        "type": "STATE_UPDATE",
                        "data": {
                            "current_step": "categorizer",
                            "progress": {
                                "total": len(all_transactions),
                                "processed": len(all_transactions) - len(uncategorized_transactions(None)),
                            },
                            "summary": state.get("summary_data", {})
                        }
                    })
                    state["next_step"] = "categorizer"
                    session_store.update_session(session_id, state)
                    continue
                await websocket.send_json({
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
                        } for txn in updated_state["batch_for_feedback"]]
                    }
                })

                # Wait for feedback from frontend
                feedback = await websocket.receive_json()
                if feedback["type"] == "SUBMIT_FEEDBACK":
                    params = {
                        "session_id": session_id,
                        "transactions": feedback["data"]["transactions"]
                    }
                    update_expense_categories(params['transactions'])  # Update expense categories based on feedback

                    # Update state after feedback
                    state["next_step"] = "categorizer"
                    session_store.update_session(session_id, state)
                else:
                    await websocket.send_json({
                        "type": "ERROR",
                        "message": "Invalid feedback received"
                    })
                    continue

            # Send progress updates to the frontend
            print("send update")
            await websocket.send_json({
                "type": "STATE_UPDATE",
                "data": {
                    "current_step": state["next_step"],
                    "progress": {
                        "total": len(all_transactions),
                        "processed": len(all_transactions) - len(uncategorized_transactions(None)),
                    },
                    "summary": state.get("summary_data", {})
                }
            })

            # Check for workflow completion
            if state["next_step"] == "end":
                await websocket.send_json({
                    "type": "COMPLETE",
                    "data": {
                        "summary": state.get("summary_data", {}),
                        "progress": {
                            "total": len(all_transactions),
                            "processed": len(all_transactions) - len(uncategorized_transactions(None)),
                        },
                        "message": "Workflow completed successfully"
                    }
                })
                break

            # Wait before proceeding to next step (simulate processing delay)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        raise Exception(e)
        await websocket.send_json({
            "type": "ERROR",
            "message": str(e)
        })

    finally:
        await websocket.close()
