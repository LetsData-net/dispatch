from typing import Optional
from pydantic import BaseModel


class ButtonValue(BaseModel):
    organization_slug: str = "default"
    incident_id: str
    action_type: str


class TaskButton(ButtonValue):
    resource_id: str


class MonitorButton(ButtonValue):
    weblink: str
    plugin_instance_id: int


class SubjectMetadata(BaseModel):
    id: Optional[str]
    type: Optional[str]
    organization_slug: str
    project_id: Optional[str]
    channel_id: Optional[str]
