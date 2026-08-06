from pydantic import BaseModel


class WidgetCreate(BaseModel):
    title: str
    description: str
    widget_type: str
    button_text: str


class WidgetResponse(BaseModel):
    id: int
    title: str
    description: str
    widget_type: str
    button_text: str
    is_active: bool

    class Config:
        from_attributes = True

class WidgetResponse(BaseModel):
    id: int
    title: str
    description: str
    widget_type: str
    button_text: str
    is_active: bool

    class Config:
        from_attributes = True

