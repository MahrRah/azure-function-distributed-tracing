import os
import time
import uuid
from typing import Iterable

from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.storage.queue import QueueClient
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider, get_meter_provider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


configure_azure_monitor(
    connection_string="InstrumentationKey=e0b953a4-46b9-48af-bc40-2fa8654c8806;IngestionEndpoint=https://switzerlandnorth-0.in.applicationinsights.azure.com/;LiveEndpoint=https://switzerlandnorth.livediagnostics.monitor.azure.com/;ApplicationId=943aac6a-26de-4afc-98b9-6e80207a00fd"
)


def get_client():
    queue_name = "baar"
    storage_account_name = "ammssa"
    account_url = f"https://{storage_account_name}.queue.core.windows.net"
    default_credential = DefaultAzureCredential()

    return QueueClient(
        account_url, queue_name=queue_name, credential=default_credential
    )


def get_queue_length():
    try:
        print("Azure Queue storage - Python quickstart sample")
        client = get_client()
        properties = client.get_queue_properties()
        count = properties.approximate_message_count
        print("Message count: " + str(count))
        return count
    except Exception as ex:
        print("Exception:")
        print(ex)

queue_length_gauge = None

def get_queue_length_callback(_: CallbackOptions):
    value = get_queue_length()
    yield Observation(value)


def generate_metric():

    meter = get_meter_provider().get_meter("test_meter")
    queue_length_gauge = meter.create_gauge("gauge")
    queue_length_gauge = meter.create_observable_gauge(
        callbacks=[get_queue_length_callback],
        name="queue_length",
        description="Queue length",
        unit="1",
    )

    try:
        while True:
            print("waiting for 1 minute")
            length = get_queue_length()
            queue_length_gauge.set(length)
            time.sleep(60)  # Delay for 1 minute
    except KeyboardInterrupt:
        print("shutting down...")


if __name__ == "__main__":
    generate_metric()


# implement sync gaug https://github.com/open-telemetry/opentelemetry-python/pull/3462/files
