import os

from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient
from opentelemetry.metrics import CallbackOptions, Observation


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
        properties = client.get_queue_properties()
        count = properties.approximate_message_count
        print("Message count: " + str(count))
        return count
    except Exception as ex:
        print("Exception:")
        print(ex)


def get_queue_length_callback(_: CallbackOptions):
    client = get_client()
    value = get_queue_length(client)
    yield Observation(value, attributes={"pid": os.getpid()})
