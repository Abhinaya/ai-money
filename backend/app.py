from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from uiflow import router as flow_router
from session import SessionStore

app = FastAPI()
session_store = SessionStore()

app.include_router(flow_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
