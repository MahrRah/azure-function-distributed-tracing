import logging

import azure.durable_functions as df
import azure.functions as func
from opentelemetry import trace
from opentelemetry.propagate import extract

# To learn more about blueprints in the Python prog model V2,
# see: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators#blueprints

bp = df.Blueprint()

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


@bp.route(route="handlers")
@bp.durable_client_input(client_name="client")
async def start_orchestrator(req: func.HttpRequest, client, context):
    carrier = {
        "traceparent": context.trace_context.Traceparent,
        "tracestate": context.trace_context.Tracestate,
    }

    # This manual trace context is needed to correlate the host logs with the ones from the worker
    with tracer.start_as_current_span(
        "start_orchestrator",
        context=extract(carrier),
    ):
        logger.info("Starting new orchestration client")
        instance_id = await client.start_new("my_orchestrator")

        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return client.create_check_status_response(req, instance_id)


@bp.orchestration_trigger(context_name="context")
def my_orchestrator(context: df.DurableOrchestrationContext):
    logger.info("Enter orchestration method")
    logger.info("Call first action being called")
    result1 = yield context.call_activity("say_hello", "Tokyo")
    logger.info("Call second action being called")
    result2 = yield context.call_activity("say_hello", "Seattle")
    logger.info("Call third action being called")
    result3 = yield context.call_activity("say_hello", "London")
    logger.info("Finish orchestration method")
    return [result1, result2, result3]


@bp.activity_trigger(input_name="city")
def say_hello(city: str) -> str:
    logger.info("Enter activity method")
    return f"Hello {city}!"
