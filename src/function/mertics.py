import datetime
import logging

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient
from opentelemetry.metrics import get_meter_provider


metrics_bp = func.Blueprint()


logger = logging.getLogger(__name__)
queue_length_gauge = (
    get_meter_provider()
    .get_meter("storage_account_meter")
    .create_gauge("queue-length-gauge")
)


def get_queue_length():
    try:
        #TODO: move this into a config file `queue_name` and `storage_account_name`
        #TODO: client should only be created once as a singleton
        queue_name = "baar"
        storage_account_name = "ammssa"
        account_url = f"https://{storage_account_name}.queue.core.windows.net"
        default_credential = DefaultAzureCredential()

        client = QueueClient(
            account_url, queue_name=queue_name, credential=default_credential
        )

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
    length = get_queue_length()
    queue_length_gauge.set(length)
    logger.info("end timer run for metrics")
