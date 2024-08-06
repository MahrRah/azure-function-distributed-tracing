
import azure.functions as func
# from azure.monitor.opentelemetry import configure_azure_monitor
from durable_function import bp
from health import health_bp
# from observability_exporters import setup_telemetry_export
from metrics import queue_metrics_monitor_blueprint

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.register_functions(bp)
app.register_functions(health_bp)
# app.register_functions(metrics_bp)
app.register_functions(queue_metrics_monitor_blueprint)
