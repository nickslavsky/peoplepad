from pydantic import BaseModel, ConfigDict
from uuid import UUID

class TagResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)