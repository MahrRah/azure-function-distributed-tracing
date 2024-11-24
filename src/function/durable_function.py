import logging
import uuid
import json
import re

import azure.durable_functions as df
import azure.functions as func

from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.trace import Span, SpanContext, SpanKind, get_current_span

# To learn more about blueprints in the Python prog model V2,
# see: https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators#blueprints

bp = df.Blueprint()

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


@bp.route(route="handlers")
@bp.durable_client_input(client_name="client")
async def start_orchestrator(req: func.HttpRequest, client, context):

    traceparent = context.trace_context.Traceparent
    current_span = get_current_span()

    carrier = {
        "traceparent": context.trace_context.Traceparent,
        "tracestate": context.trace_context.Tracestate,
    }
    
    with tracer.start_as_current_span(
        "start_orchestrator", kind=SpanKind.SERVER, context=extract(carrier)
    ) as span:

        logger.info(f"start_orchestration received {traceparent}")
        logger.info(f"start_orchestration current trace_id:{current_span._context.trace_id}, span_id:{current_span._context.span_id}")
        
        job_id = str(uuid.uuid4())
        child_span = _extract_context(span)

        logger.info(f"start_orchestation: child_trace_id:{child_span['trace_id']}, child_span_id:{child_span['span_id']}")

        instance_id = await client.start_new(
            "my_orchestrator", instance_id=job_id, client_input=child_span
        )

        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return client.create_check_status_response(req, instance_id)


@bp.orchestration_trigger(context_name="context")
def my_orchestrator(context: df.DurableOrchestrationContext):

    trace_context = context.get_input()
    logger.info("Call first action being called")
    aml_job_id = yield context.call_activity(
        "say_hello", {"city": "Tokyo", "trace_context": trace_context}
    )

    print(f"aml_job_id: {aml_job_id}")

    logger.info("Persist entity state")
    entityId = df.EntityId("main_entity", aml_job_id)
    yield context.call_entity(entityId, "set", trace_context)

    return aml_job_id


@bp.activity_trigger(input_name="body")
def say_hello(body: dict, context: func.Context) -> str:

        logger.info(f"say_hello")
        aml_job_id = str(uuid.uuid4())
        return f"{aml_job_id}"


@bp.entity_trigger(context_name="context", entity_name="main_entity")
def persist_entity_state(context: df.DurableEntityContext) -> None:

    trace_context = context.get_input()
    ctx = _create_context(trace_context)
    with tracer.start_as_current_span("set_entity", context=ctx):
        operation = context.operation_name
        if operation == "set":
            context.set_state(trace_context)


@bp.queue_trigger(
    arg_name="amlEventQueueMessage",
    queue_name="aml-events",
    connection="AML_EVENTS_QUEUE_CONNECTION",
)
@bp.queue_output(
    arg_name="apiEventOutputBinding",
    queue_name="api-events",
    connection="API_EVENTS_QUEUE_CONNECTION",
)
@bp.durable_client_input(client_name="client")
async def process_aml_event(
    amlEventQueueMessage: func.QueueMessage,
    client: df.DurableOrchestrationClient,
    apiEventOutputBinding: func.Out[str],
    context,
) -> None:
    
    aml_job_id = amlEventQueueMessage.get_body().decode('utf-8')

    entity_id = df.EntityId("main_entity", aml_job_id)
    entity = await client.read_entity_state(entity_id)

    ctx = _create_context(entity.entity_state)
    with tracer.start_as_current_span("process_aml_message", kind=SpanKind.PRODUCER, context=ctx) as span:
        
        logger.info("About to process inbound queue message")

        child_span = _extract_context(span)
        apiEventOutputBinding.set(json.dumps(child_span))


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