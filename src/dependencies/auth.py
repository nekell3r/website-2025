from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel


from src.services.auth import AuthService


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


PaginationDep = Annotated[PaginationParams, Depends()]

def get_current_user_dp(dp: str):
    async def dependency(
        payload: dict = Depends(AuthService().get_token),

    ):
        return payload[dp]
    return dependency



UserIdDep = Annotated[int, Depends(get_current_user_dp("id"))]
UserRoleDep = Annotated[bool, Depends(get_current_user_dp("is_super_user"))]



