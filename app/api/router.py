from fastapi import APIRouter
from app.api.v1.endpoints import auth, agents, sessions

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(agents.router)
api_router.include_router(sessions.router)