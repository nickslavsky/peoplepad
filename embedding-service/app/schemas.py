from pydantic import BaseModel

class EmbedRequest(BaseModel):
    input: str
    model: str
    encoding_format: str

class BatchInput(BaseModel):
    id: str
    text: str

class BatchRequest(BaseModel):
    inputs: list[BatchInput]
    model: str
    encoding_format: str