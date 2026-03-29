from pydantic import BaseModel


class ComponentStatus(BaseModel):
    name: str
    ok: bool
    detail: str


class ReadinessResponse(BaseModel):
    status: str
    components: list[ComponentStatus]
    models: dict
