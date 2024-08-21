import json
from typing import List, Optional
 
from pydantic import Field, BaseModel, field_validator, validator
from pydantic_settings import BaseSettings
 
class MonitorQueueInformation(BaseModel):
    storage_account_url: str
    queue_name: str
    key: Optional[str] = None
 
 
class MonitorSettings(BaseSettings):
    MONITORING_SCHEDULE_CRON: Optional[str] = Field(description="Primary hostname for the app.", default="0 */10 * * * *")
    MONITORED_QUEUES: List[MonitorQueueInformation] = Field(..., description="List of connections to be monitored.")
 
    # @field_validator('MONITORED_QUEUES',mode='before')
    # def parse_connections(cls, v):
    #     if isinstance(v, str):
    #         return v
    #     return v
    
  
if __name__ == "__main__":
    settings = MonitorSettings()
    print(settings.MONITORED_QUEUES)
    print(settings.MONITORING_SCHEDULE_CRON)
