from fastapi import APIRouter
from src.api import legacy, v1

router = APIRouter()
router.include_router(v1.router)
router.include_router(legacy.router)
