from fastapi import APIRouter

from src.api.v1 import feedback, hiscore, label, player, prediction, report, scraper

router = APIRouter()
router.include_router(feedback.router)
router.include_router(hiscore.router)
router.include_router(label.router)
router.include_router(player.router)
router.include_router(prediction.router)
router.include_router(report.router)
router.include_router(scraper.router)
