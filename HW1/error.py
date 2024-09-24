from typing import Callable

async def send_error(stat: int, send: Callable) -> None:
    dict = {400: b'{"detail": "Bad Request"}',
            404: b'{"detail": "Not found"}',
            422: b'{"detail": "Unprocessable Entity"}'}
    await send({
        "type": "http.response.start",
        "status": stat,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({
        "type": "http.response.body",
        "body": dict[stat],
    })