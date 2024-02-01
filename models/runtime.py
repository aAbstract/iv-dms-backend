from pydantic import BaseModel


class ServiceResponse(BaseModel):
    success: bool = True
    status_code: int = 200
    msg: str = ''
    data: dict = {}
