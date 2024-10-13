from fastapi import FastAPI, Request
from hw_2.routers.quaries import router_cart, router_item
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="Shop API")

app.include_router(router_cart)
app.include_router(router_item)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=["*"], allow_methods=["*"], allow_headers=["*"])

REQUEST_COUNT = Counter("app_requests_total", "Total number of requests")
REQUEST_DURATION = Histogram("app_request_duration_seconds", "Duration of requests in seconds")
ERROR_COUNT = Counter("app_errors_total", "Total number of errors")


@app.middleware("http")
async def add_prometheus_metrics(request: Request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_DURATION.time():
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                ERROR_COUNT.inc()
            return response
        except Exception as e:
            ERROR_COUNT.inc()
            raise e


Instrumentator().instrument(app).expose(app)