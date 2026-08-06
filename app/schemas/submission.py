from pydantic import BaseModel, EmailStr


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

    class Config:
        from_attributes = True