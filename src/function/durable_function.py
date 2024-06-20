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

    # pattern = re.compile(r"00-(\w+)-(\w+)-\d+")
    # match = pattern.match(traceparent)
    # if match:
    #     trace_id_hex, span_id_hex = match.groups()
    #     parent_trace_id = int(trace_id_hex, 16)
    #     parent_span_id = int(span_id_hex, 16)
    #     logger.info(f"handlers / start_orchestration received trace_id:{parent_trace_id}, span_id:{parent_span_id}")

    carrier = {
        "traceparent": context.trace_context.Traceparent,
        "tracestate": context.trace_context.Tracestate,
    }
    
    # This manual trace context is needed to correlate the host logs with the ones from the worker
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

    ctx = _create_context(context.get_input())
    current_span = get_current_span()

    with tracer.start_as_current_span("my_orchestrator", context=ctx) as span:

        logger.info(f"my_orchestrator current trace_id:{current_span._context.trace_id}, span_id:{current_span._context.span_id}")

        log_received_ctx(ctx, "my_orchestrator")

        child_span = _extract_context(span)
        logger.info(f"my_orchestrator: child_trace_id:{child_span['trace_id']}, child_span_id:{child_span['span_id']}")

        logger.info("Call first action being called")
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

        logger.info("Persist entity state")
        entityId = df.EntityId("main_entity", 1)
        yield context.call_entity(entityId, "set", child_span)

        return [result1, result2, result3]


@bp.activity_trigger(input_name="body")
def say_hello(body: dict, context: func.Context) -> str:

    current_span = get_current_span()
    ctx = _create_context(body["trace_context"])

    with tracer.start_as_current_span("say_hello", context=ctx) as span:
        logger.info(f"say_hello current traceparent: {context.trace_context.trace_parent}")
        logger.info(f"say_hello current trace_id:{current_span._context.trace_id}, span_id:{current_span._context.span_id}")
        
        child_span = _extract_context(span)
        logger.info(f"say_hello: child_trace_id:{child_span['trace_id']}, child_span_id:{child_span['span_id']}")
        log_received_ctx(ctx, "say_hello")
        return f"Hello {body['city']}!"


@bp.entity_trigger(context_name="context", entity_name="main_entity")
def persist_entity_state(context: df.DurableEntityContext) -> None:

    current_span = get_current_span()
    ctx = _create_context(context.get_input())

    with tracer.start_as_current_span("set_entity", context=ctx):
        logger.info(f"persist_entity_state current trace_id:{current_span._context.trace_id}, span_id:{current_span._context.span_id}")
        log_received_ctx(ctx, "persist_entity_state")
        operation = context.operation_name
        if operation == "set":
            context.set_state(context.get_input())


@bp.queue_trigger(
    arg_name="amlEventQueueMessage",
    queue_name="spike-aml-events",
    connection="AML_EVENTS_QUEUE_CONNECTION",
)
@bp.queue_output(
    arg_name="apiEventOutputBinding",
    queue_name="spike-api-events",
    connection="API_EVENTS_QUEUE_CONNECTION",
)
@bp.durable_client_input(client_name="client")
async def process_aml_event(
    amlEventQueueMessage: func.QueueMessage,
    client: df.DurableOrchestrationClient,
    apiEventOutputBinding: func.Out[str],
    context,
) -> None:
    
    carrier = {
        "traceparent": context.trace_context.Traceparent,
        "tracestate": context.trace_context.Tracestate,
    }

    logger.info(f"process_aml_events queue_trigger received {context.trace_context.Traceparent}")

    with tracer.start_as_current_span("queue_trigger", kind=SpanKind.PRODUCER, context=extract(carrier)) as span:
        
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


def log_received_ctx(ctx, prefix: str):
    key = ''
    for element in ctx:
        key = element
        break

    ctx_trace_id = ctx[key]._context.trace_id
    ctx_span_id = ctx[key]._context.span_id

    logger.info(f"{prefix} received trace_id:{ctx_trace_id}, span_id:{ctx_span_id}")

