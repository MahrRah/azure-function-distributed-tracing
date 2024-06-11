import logging
import os

import handler
from fastapi import FastAPI
from observability_exporters import setup_telemetry_export
from opentelemetry.instrumentation.aiohttp_client import \
    AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

app = FastAPI()

root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

setup_telemetry_export(
    service_name="api-service",
    service_instance_id="instance-1",
    service_version="1.0.0",
    application_insights_connection_string=os.environ.get(
        "APPLICATIONINSIGHTS_CONNECTION_STRING"
    ),
    logger=root_logger,
)

app.include_router(handler.router)

FastAPIInstrumentor.instrument_app(app)
AioHttpClientInstrumentor().instrument()
RequestsInstrumentor().instrument()
URLLib3Instrumentor().instrument()
