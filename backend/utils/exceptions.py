from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from utils.responses import create_response


def exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException):
        response = create_response(request, exc.status_code, exc.detail, None, str(exc))
        return JSONResponse(status_code=exc.status_code, content=response.model_dump())

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):
        response = create_response(request, status.HTTP_422_UNPROCESSABLE_CONTENT, "Lỗi Validate", None, {
                "type": exc.errors()[0]["type"],
                "msg": exc.errors()[0]["msg"]
                })
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=response.model_dump())

    @app.exception_handler(Exception)
    def global_exception_handler(request: Request, exc: Exception):
        response = create_response(
            request, status.HTTP_500_INTERNAL_SERVER_ERROR, "Lỗi", None, str(exc))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response.model_dump())
