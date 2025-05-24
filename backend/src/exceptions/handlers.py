from fastapi import Request
from fastapi.responses import JSONResponse
from src.exceptions.service_exceptions import MadRussianServiceException


async def mad_russian_service_exception_handler(request: Request, exc: MadRussianServiceException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    ) 