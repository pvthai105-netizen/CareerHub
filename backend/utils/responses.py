from fastapi import Request
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class BaseResponse(BaseModel):
    statusCode: int
    message: str
    error: Optional[Any]
    data: Optional[Any]
    path: str
    timestamp: str


def create_response(request: Request, status_code: int, message: str, data: Any | None = None, error: Any | None = None):
    return BaseResponse(
        statusCode=status_code,
        message=message,
        error=error,
        data=data,
        path=request.url.path,
        timestamp=datetime.now().isoformat()
    )