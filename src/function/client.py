from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    storage_account_name: str = Field(validation_alias="STORAGE_ACCOUNT")
    queue_name: str = Field(validation_alias="QUEUE_NAME")


def get_queue_client():
    try:
        setting = Settings()
        account_url = f"https://{setting.storage_account_name}.queue.core.windows.net"
        default_credential = DefaultAzureCredential()

        queue_client = QueueClient(
            account_url, queue_name=setting.queue_name, credential=default_credential
        )
        return queue_client
    except Exception as ex:
        print(ex)
