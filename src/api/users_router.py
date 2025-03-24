import sys

from fastapi import APIRouter, Body
from pathlib import Path
from sqlalchemy import insert

from src.database import async_session_maker
from src.schemas.schemas import ReviewSchema
from src.models.reviews import ReviewsORM

sys.path.append(str(Path(__file__).parent.parent))

router = APIRouter()
