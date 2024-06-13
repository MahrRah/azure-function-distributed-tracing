import logging
import uuid

import azure.durable_functions as df
import azure.functions as func
from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.trace import Span, SpanContext

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
        "start_orchestrator", context=extract(carrier)
    ) as span:

        logger.info("Starting new orchestration client")
        job_id = str(uuid.uuid4())
        child_span = _extract_context(span)
        instance_id = await client.start_new(
            "my_orchestrator", instance_id=job_id, client_input=child_span
        )

        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return client.create_check_status_response(req, instance_id)


@bp.orchestration_trigger(context_name="context")
def my_orchestrator(context: df.DurableOrchestrationContext):
    ctx = _create_context(context.get_input())

    with tracer.start_as_current_span("my_orchestrator", context=ctx) as span:
        logger.info("Enter orchestration method")
        logger.info("Call first action being called")
        child_span = _extract_context(span)
        result1 = yield context.call_activity(
            "say_hello", {"city": "Tokyo", "trace_context": child_span}
        )
        logger.info("Call second action being called")
        result2 = yield context.call_activity(
            "say_hello", {"city": "Seattle", "trace_context": child_span}
        )
        logger.info("Call third action being called")
        result3 = yield context.call_activity(
            "say_hello", {"city": "London", "trace_context": child_span}
        )
        logger.info("Finish orchestration method")
        return [result1, result2, result3]


@bp.activity_trigger(input_name="body")
def say_hello(body: dict, context: func.Context) -> str:
    ctx = _create_context(body["trace_context"])
    with tracer.start_as_current_span("say_hello", context=ctx):
        logger.info("Enter activity method")
        return f"Hello {body['city']}!"


def _extract_context(span: Span):
    ctx = span.get_span_context()
    return {
        "trace_id": ctx.trace_id,
        "span_id": ctx.span_id,
    }


def _create_context(span_context):
    span_ctx = SpanContext(
        trace_id=span_context["trace_id"],
        span_id=span_context["span_id"],
        is_remote=True,
    )
    return trace.set_span_in_context(trace.NonRecordingSpan(span_ctx))
