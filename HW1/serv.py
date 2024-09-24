import json
from typing import Any, Callable, Dict
from urllib.parse import parse_qs

from .math import factorial, fibonacci, mean
from .error import send_error


async def app(scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
    if scope["type"] != "http":
        return
    
    method: str = scope["method"]
    path: str = scope["path"]
    
    if path.startswith("/factorial") and method == "GET":
        await handle_factorial(scope, send)
        return
    
    if path.startswith("/fibonacci") and method == "GET":
        await handle_fibonacci(path, send)
        return
    
    if path.startswith("/mean") and method == "GET":
        await handle_mean(receive, send)
        return
    
    await send_error(404, send)
    

async def read_body(receive: Callable) -> bytes:
    body = b""
    
    while True:
        message = await receive()
        
        body += message.get("body", b'')
        if not message.get("more_body", False):
            break
    
    return body

async def send_json(send, data, status=200):
    body = json.dumps(data).encode("utf8")
    
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json")]
    })
    await send({
        "type": "http.response.body",
        "body": body,
    })
    
async def handle_factorial(scope: Dict[str, Any], send: Callable) -> None:
    query_string = scope["query_string"].decode()
    params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
    n = params.get("n", 0)
    
    if not n:
        await send_error(422, send)
        return
    
    try:
        int_n = int(n)
    except ValueError:
        await send_error(422, send)
        return

    if int_n < 0:
        await send_error(400, send)
        return
    
    await send_json(send, {"result": factorial(int_n)})
    return
    

    

async def handle_fibonacci(path: str, send: Callable) -> None:
    try:
        n = int(path.split("/")[-1])
    
    except ValueError:
        await send_error(422, send)
        return
    
    if n < 0:
        await send_error(400, send)
        return
    
    await send_json(send, {"result": fibonacci(n)})
    return
    
    

async def handle_mean(receive: Callable, send: Callable) -> None:
    body = await read_body(receive)
    try:
        nyms = json.loads(body)
        
        if len(nyms) == 0:
            await send_error(400, send)
            return
        
        if not isinstance(nyms, list) or not all(isinstance(num, (int, float)) for num in nyms):
            await send_error(422, send)
            return
        
        await send_json(send, {"result": mean(nyms)})
        return
    
    except (json.JSONDecodeError, TypeError):
        await send_error(422, send)
        return
        