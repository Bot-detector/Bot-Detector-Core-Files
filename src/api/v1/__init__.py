from fastapi import APIRouter

from src.api.v1 import feedback, hiscore, label, player, prediction, report, scraper

router = APIRouter()
router.include_router(feedback.router, prefix="/v1")
router.include_router(hiscore.router, prefix="/v1")
router.include_router(label.router, prefix="/v1")
router.include_router(player.router, prefix="/v1")
router.include_router(prediction.router, prefix="/v1")
router.include_router(report.router, prefix="/v1")
router.include_router(scraper.router, prefix="/v1")
