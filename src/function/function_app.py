
import azure.functions as func
from health import health_bp

from metrics import queue_metrics_monitor_blueprint

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
# app.register_functions(bp)
app.register_functions(health_bp)
app.register_functions(queue_metrics_monitor_blueprint)
