from pydantic import BaseModel, model_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Any

class RecordCreate(BaseModel):
    name: str
    notes: Optional[str] = None
    tags: List[str] = []

class RecordUpdate(BaseModel):
    name: str
    notes: Optional[str] = None
    tags: List[str] = []

class RecordResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    notes: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def convert_tags(cls, data: Any) -> Any:
        # If data is an ORM object with a 'tags' attribute, convert to dict and transform tags
        if hasattr(data, 'tags'):
            # Convert ORM object to dict, preserving all attributes
            data_dict = {key: getattr(data, key) for key in data.__dict__ if not key.startswith('_')}
            # Transform tags to list of strings
            data_dict['tags'] = [tag.name for tag in data.tags or []]
            return data_dict
        return data