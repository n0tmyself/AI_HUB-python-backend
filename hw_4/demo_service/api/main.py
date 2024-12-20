from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from hw_4.demo_service.api import users, utils


def create_app():
    app = FastAPI(
        title="Testing Demo Service",
        lifespan=utils.initialize,
    )

    app.add_exception_handler(ValueError, utils.value_error_handler)
    app.include_router(users.router)

    return app


app = create_app()
Instrumentator().instrument(app).expose(app)