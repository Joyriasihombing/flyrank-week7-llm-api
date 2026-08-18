from pydantic import BaseModel, EmailStr, ConfigDict


class SubmissionCreate(BaseModel):
    name: str
    email: EmailStr
    message: str


class SubmissionResponse(BaseModel):
    id: int
    widget_id: int
    name: str
    email: EmailStr
    message: str

    category: str
    urgency: str
    confidence: float
    reason: str | None = None

    model_config = ConfigDict(from_attributes=True)