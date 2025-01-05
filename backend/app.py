from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from uiflow import router as flow_router
from transactions_api import router as transactions_router

app = FastAPI()

# Middleware to strip `/api` from the path
@app.middleware("http")
async def rewrite_api_path(request: Request, call_next):
    if request.url.path.startswith("/api"):
        scope = request.scope
        scope["path"] = request.url.path[len("/api") :]
        request = Request(scope, request.receive)
    response = await call_next(request)
    return response

app.include_router(flow_router)
app.include_router(transactions_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
