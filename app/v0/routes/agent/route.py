import logging

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.v0.routes.agent.request_models import AgentRequest
from app.v0.routes.agent.response_models import ChatResponse
from core.chat.service import chat as run_chat
from core.stream.service import stream as run_stream


logger = logging.getLogger(__name__)

agent_router = APIRouter()


@agent_router.post('/chat', response_model = ChatResponse)
async def chat(request: AgentRequest):
    try:
        output = await run_chat(request.user_query)
        return ChatResponse(output = output)
    except Exception as e:
        logger.exception('Error in chat')
        raise HTTPException(status_code = 500, detail = str(e)) from e


@agent_router.post('/stream')
async def stream(request: AgentRequest):
    async def generate_sse_events():
        try:
            async for fragment in run_stream(request.user_query):
                yield fragment.to_sse().encode()
        except Exception:
            logger.exception('Error in SSE stream')
            raise

    return EventSourceResponse(generate_sse_events())
