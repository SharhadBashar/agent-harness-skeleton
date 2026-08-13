from fastapi import APIRouter

from app.v0.routes.agent.route import agent_router


v0_router = APIRouter()

v0_router.include_router(agent_router, prefix = '/agent', tags = ['Agent'])
