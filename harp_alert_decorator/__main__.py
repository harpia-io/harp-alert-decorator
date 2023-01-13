import harp_alert_decorator.settings as settings
from fastapi import FastAPI, Request, status
from prometheus_fastapi_instrumentator import Instrumentator
from harp_alert_decorator.api.health import router as health
from harp_alert_decorator.api.consumer import router as consumer
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from harp_alert_decorator.plugins.tracer import get_tracer
from logger.logging import fastapi_logging
from fastapi.exceptions import RequestValidationError
from logger.logging import service_logger
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

log = service_logger()
fastapi_logging()
tracer = get_tracer()

app = FastAPI(
    openapi_url=f'{settings.URL_PREFIX}/openapi.json',
    docs_url=f'{settings.URL_PREFIX}/docs',
    redoc_url=f'{settings.URL_PREFIX}/redoc'
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log.error(
        msg=f"FastAPI: Failed to validate request\nURL: {request.method} - {request.url}\nBody: {exc.body}\nError: {exc.errors()}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
Instrumentator().instrument(app).expose(app)
app.include_router(health)
app.include_router(consumer)
