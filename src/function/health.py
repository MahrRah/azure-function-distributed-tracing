import logging

import azure.functions as func
from opentelemetry import trace

health_bp = func.Blueprint()

tracer = trace.get_tracer(__name__)


@health_bp.route(route="health")
def health(req: func.HttpRequest):
    logging.info("Health endpoint called.")
    return func.HttpResponse(
        "This HTTP triggered function executed successfully and Azure function is healthy",
        status_code=200,
    )
