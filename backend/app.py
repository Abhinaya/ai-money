from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from uiflow import router as flow_router
from transactions_api import router as transactions_router

app = FastAPI()

app.include_router(flow_router)
app.include_router(transactions_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
