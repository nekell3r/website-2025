import sys

from fastapi import APIRouter
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter(prefix="/buy", tags=["Покупка материалов и платежи"])
