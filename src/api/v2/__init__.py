from fastapi import APIRouter

from src.api.v2 import highscore, player

router = APIRouter(tags=["v2"])
router.include_router(highscore.router)
router.include_router(player.router)
