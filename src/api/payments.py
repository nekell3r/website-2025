import sys

from fastapi import APIRouter, Body, Response, HTTPException
from pathlib import Path

from src.api.dependencies import UserIdDep, DBDep

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/buy", tags=["Покупка материалов и платежи"])
