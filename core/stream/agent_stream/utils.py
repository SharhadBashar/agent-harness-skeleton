import ast

from core.stream.agent_stream.constants import (
    BIN_OPS,
    CITY_ALIASES,
    SUPPORTED_CITIES,
    UNARY_OPS,
    WEATHER_API,
)


def _eval_math_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_math_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
        return UNARY_OPS[type(node.op)](_eval_math_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
        return BIN_OPS[type(node.op)](
            _eval_math_node(node.left),
            _eval_math_node(node.right),
        )
    raise ValueError('Unsupported math expression')


def get_weather(city: str) -> dict:
    '''Look up current weather from the dummy weather API.

    Supported cities: New York, London, Tokyo, Toronto, Sydney.
    '''
    key = city.strip().lower()
    key = CITY_ALIASES.get(key, key)
    weather = WEATHER_API.get(key)
    if weather is None:
        return {
            'error': f'Weather not available for {city}.',
            'supported_cities': SUPPORTED_CITIES,
        }
    return weather


def calculate(expression: str) -> dict:
    '''Evaluate a numeric math expression.

    Supports +, -, *, /, //, %, ** and parentheses.
    '''
    try:
        parsed = ast.parse(expression.strip(), mode = 'eval')
        result = _eval_math_node(parsed)
    except ZeroDivisionError:
        return {'expression': expression, 'error': 'Division by zero'}
    except (SyntaxError, ValueError, TypeError) as e:
        return {'expression': expression, 'error': str(e)}
    return {'expression': expression, 'result': result}
