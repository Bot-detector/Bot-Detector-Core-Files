from fastapi import APIRouter

from src.api.v2 import highscore

router = APIRouter()
router.include_router(highscore.router)
