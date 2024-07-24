import datetime
import logging

import azure.functions as func
from azure.storage.queue import QueueClient
from client import get_queue_client
from opentelemetry.metrics import get_meter_provider

metrics_bp = func.Blueprint()


logger = logging.getLogger(__name__)
queue_length_gauge = (
    get_meter_provider()
    .get_meter("storage_account_meter")
    .create_gauge("queue-length-gauge")
)

from opentelemetry import trace

client = get_queue_client()


def get_queue_length(client: QueueClient):
    try:
        ctx = trace.get_current_span()
        ctx.set_attribute("custom_attribute", "custom_value")

        
        properties = client.get_queue_properties()
        count = properties.approximate_message_count
        logger.info("Message count: " + str(count))
        return count
    except Exception as ex:
        logger.error("Exception:")
        logger.error(ex)


@metrics_bp.function_name(name="mytimer")
@metrics_bp.timer_trigger(
    schedule="*/30 * * * * *", arg_name="mytimer", run_on_startup=False
)
def run_metrics(mytimer: func.TimerRequest):
    logger.info("enter trigger")
    if mytimer.past_due:
        logger.info("past due")
    logger.info("starting timer run for metrics")
    length = get_queue_length(client)
    queue_length_gauge.set(length)
    logger.info("end timer run for metrics")
