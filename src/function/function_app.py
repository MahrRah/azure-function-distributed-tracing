import logging
import os

import azure.functions as func
from durable_function import bp
from health import health_bp
from observability_exporters import setup_telemetry_export
from opentelemetry.instrumentation.aiohttp_client import \
    AioHttpClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("azure").setLevel(logging.WARNING)

AioHttpClientInstrumentor().instrument()
RequestsInstrumentor().instrument()
URLLib3Instrumentor().instrument()


setup_telemetry_export(
    service_name="orchestration-function",
    service_instance_id="instance-1",
    service_version="1.0.0",
    application_insights_connection_string=os.getenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING", None
    ),
    logger=root_logger,
)


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.register_functions(bp)
app.register_functions(health_bp)
