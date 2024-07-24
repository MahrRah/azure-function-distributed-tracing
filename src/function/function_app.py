import logging
import os

import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor
from durable_function import bp
from health import health_bp
from mertics import metrics_bp
from observability_exporters import setup_telemetry_export

root_logger = logging.getLogger()
for handlers in root_logger.handlers[:]:
    root_logger.removeHandler(handlers)

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

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.register_functions(bp)
app.register_functions(health_bp)
app.register_functions(metrics_bp)
