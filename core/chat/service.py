from core.chat.agent_chat.agents import chat_agent


async def chat(user_query: str) -> str:
    result = await chat_agent.run(user_query)
    return str(result.output)
