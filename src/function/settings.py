from typing import List, Optional
from pydantic import BaseModel, field_validator
from pydantic.fields import Field
from pydantic_settings import BaseSettings
import json


class MonitorQueueInformation(BaseModel):
    storage_account_url: str
    queue_name: str
    storage_account_key: Optional[str] = None
 
 
class MonitorSettings(BaseSettings):
    MONITORING_SCHEDULE_CRON: str = Field(
        default="0 */10 * * * *",
        description="Cron expression to define queue monitoring interval",
    )
    MONITORED_QUEUES: List[MonitorQueueInformation] = Field(..., description="List of queues to be monitored.")
 
    @field_validator("MONITORED_QUEUES", mode="before", check_fields=False)
    def parse_connections(cls, v: str):  # noqa: N805
        if isinstance(v, str):
            return json.loads(v)
        return v
 