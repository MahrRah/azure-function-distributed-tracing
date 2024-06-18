import logging

import azure.functions as func
from opentelemetry import trace

test_bp = func.Blueprint()

tracer = trace.get_tracer(__name__)


@test_bp.route(route="regular-handlers")
def do_something(req: func.HttpRequest):
    logging.info("Test endpoint called.")
    do_something_more()
    return func.HttpResponse(
        "Test endpoint called successfully.",
        status_code=200,
    )


def do_something_more():
    logging.info("Starting to do stuff.")
    with tracer.start_as_current_span("do_something_more"):
        logging.info("Doing stuff has been successful.")
        return True
