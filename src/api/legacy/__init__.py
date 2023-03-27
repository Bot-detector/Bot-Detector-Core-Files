from fastapi import APIRouter

from src.api.legacy import legacy, legacy_debug

router = APIRouter()

router.include_router(legacy.router)
router.include_router(legacy_debug.router)
