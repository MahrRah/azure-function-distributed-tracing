import os

import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor
from durable_function import bp
from health import health_bp


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.register_functions(bp)
app.register_functions(health_bp)
