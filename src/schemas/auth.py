from pydantic import BaseModel, Field
from datetime import datetime

class JWTPayload(BaseModel):
    sub: str  # Subject (usually user ID as string)
    id: int   # User ID as integer
    is_super_user: bool = False
    exp: datetime
    type: str = Field(default="access", pattern="^(access|refresh)$") # "access" or "refresh" 