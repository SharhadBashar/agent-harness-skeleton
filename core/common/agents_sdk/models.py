import asyncio


from agents import Agent, OpenAIResponsesModel, Runner
from openai import AsyncOpenAI

from settings import OPENAI_API_KEY


agent = Agent(
    name = 'History Tutor',
    instructions = 'You answer history questions clearly and concisely.',
    model = OpenAIResponsesModel(
        model = 'gpt-4o-mini',
        openai_client = AsyncOpenAI(api_key = OPENAI_API_KEY),
    )
)
