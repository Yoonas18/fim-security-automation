# optional - not strictly required for current API; good for future validation
from pydantic import BaseModel

class Report(BaseModel):
    agent_id: str
    file: str
    event: str
