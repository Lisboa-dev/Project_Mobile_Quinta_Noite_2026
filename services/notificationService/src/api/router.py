from fastapi import APIRouter

from src.api.controllers.health_controller import router as health_router
from src.api.controllers.notification_controller import router as notification_router
from src.api.controllers.websocket_controller import router as websocket_router

router = APIRouter()
router.include_router(health_router)
router.include_router(notification_router)
router.include_router(websocket_router)
