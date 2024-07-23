import os
import time
import uuid
from typing import Iterable

from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
from azure.storage.queue import QueueClient

from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation, get_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

queue_length_gauge = (
    get_meter_provider()
    .get_meter("storage_account_meter_api")
    .create_gauge("service-queue-length-gauge")
)

def get_client():
    queue_name = "baar"
    storage_account_name = "ammssa"
    account_url = f"https://{storage_account_name}.queue.core.windows.net"
    default_credential = DefaultAzureCredential()

    return QueueClient(
        account_url, queue_name=queue_name, credential=default_credential
    )


def get_queue_length(client: QueueClient):
    try:
        print("Azure Queue storage - Python quickstart sample")
        properties = client.get_queue_properties()
        count = properties.approximate_message_count
        print("Message count: " + str(count))
        return count
    except Exception as ex:
        print("Exception:")
        print(ex)


def generate_metric():


    try:
        while True:
            print("waiting for 1 minute")
            client = get_client()
            length = get_queue_length(client)
            queue_length_gauge.set(length)
            time.sleep(60)  # Delay for 1 minute
    except KeyboardInterrupt:
        print("shutting down...")
