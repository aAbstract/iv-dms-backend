from pydantic import BaseModel


class JsonResponse(BaseModel):
    success: bool = True
    msg: str = ''
    data: dict = {}
