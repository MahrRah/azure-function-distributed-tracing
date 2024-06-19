import logging
import os
import asyncio
import json
import base64

import handler
from fastapi import FastAPI
from observability_exporters import setup_telemetry_export
from opentelemetry.instrumentation.aiohttp_client import \
    AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

from opentelemetry import trace
from opentelemetry.trace import SpanContext

from azure.storage.queue import QueueClient
from typing import Any, Set

app = FastAPI()

background_tasks: Set[asyncio.Task[Any]] = set()

tracer = trace.get_tracer(__name__)

root_logger = logging.getLogger()
for _handler in root_logger.handlers[:]:
    root_logger.removeHandler(_handler)

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

app.include_router(handler.router)

FastAPIInstrumentor.instrument_app(app)
AioHttpClientInstrumentor().instrument()
RequestsInstrumentor().instrument()
URLLib3Instrumentor().instrument()

logger = logging.getLogger()

@app.on_event("startup")
async def start_up():
    logger.info("FastAPI starting")
    queue_client = QueueClient.from_connection_string("AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;", "spike-api-events")
    start_event_queue_consumer(queue_client)

def start_event_queue_consumer(queue_client: QueueClient) -> None:
    loop = asyncio.get_event_loop()
    consome_task = loop.create_task(consume_messages(queue_client))
    background_tasks.add(consome_task)

async def consume_messages(queue_client: QueueClient) -> None:
    while True:
        await process_messages(queue_client=queue_client)

async def process_messages(queue_client: QueueClient) -> None:
    messages = queue_client.receive_messages(visibility_timeout=30)
    no_message_received = True
    for message in messages:
        no_message_received = False
        
        content = base64.b64decode(message.content).decode('utf-8')
        print(content)
        logger.info(f"Processing message: {content}")

        ctx = _create_context(json.loads(content))
        with tracer.start_as_current_span("api_service", context=ctx):
            logger.info("Enter api_service_message_consumer")

        queue_client.delete_message(message=message.id, pop_receipt=message.pop_receipt)

    if no_message_received:
        await asyncio.sleep(1.0)

def _create_context(dict):
    span_ctx = SpanContext(
        trace_id=dict["trace_id"],
        span_id=dict["span_id"],
        is_remote=True
    )
    return trace.set_span_in_context(trace.NonRecordingSpan(span_ctx))

