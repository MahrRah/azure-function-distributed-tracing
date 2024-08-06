import json
from typing import List, Optional
 
from pydantic import Field, BaseModel, field_validator, validator
from pydantic_settings import BaseSettings
 
class MonitorQueueInformation(BaseModel):
    account_name: str
    queue_name: str
    key: Optional[str] = None
 
 
class MonitorSettings(BaseSettings):
    MONITORING_SCHEDULE_CRON: str = Field(description="Primary hostname for the app.")
    CONNECTIONS_TO_BE_MONITORED: List[MonitorQueueInformation] = Field(..., description="List of connections to be monitored.")
 
    @field_validator('CONNECTIONS_TO_BE_MONITORED')
    def parse_connections(self, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
 
if __name__ == "__main__":
    settings = MonitorSettings()
    print(settings.CONNECTIONS_TO_BE_MONITORED)
    print(settings.MONITORING_SCHEDULE_CRON)
