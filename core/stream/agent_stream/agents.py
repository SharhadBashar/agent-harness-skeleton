from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.toolsets import FunctionToolset

from core.common.pydantic_ai.models import gpt_5_6_luna, sonnet_5
from core.stream.agent_stream.prompt import PROMPT
from core.stream.agent_stream.utils import calculate, get_weather
from core.stream.convert_weather.capability import ConvertWeatherCapability


stream_tools = FunctionToolset(id = 'stream_tools')
stream_tools.tool(get_weather)
stream_tools.tool(calculate)

stream_agent = Agent(
    FallbackModel(sonnet_5, gpt_5_6_luna),
    name = 'stream_agent',
    instructions = PROMPT,
    toolsets = [stream_tools],
    capabilities = [
        ConvertWeatherCapability(),
    ],
    output_type = str,
)
