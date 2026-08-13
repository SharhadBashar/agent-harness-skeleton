from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.toolsets import FunctionToolset

from core.chat.agent_chat.prompt import PROMPT
from core.chat.agent_chat.utils import calculate, get_weather
from core.chat.convert_weather.capability import ConvertWeatherCapability
from core.common.pydantic_ai.models import gpt_5_6_luna, sonnet_5


chat_tools = FunctionToolset(id = 'chat_tools')
chat_tools.tool(get_weather)
chat_tools.tool(calculate)

chat_agent = Agent(
    FallbackModel(sonnet_5, gpt_5_6_luna),
    name = 'chat_agent',
    instructions = PROMPT,
    toolsets = [chat_tools],
    capabilities = [
        ConvertWeatherCapability(),
    ],
    output_type = str,
)
