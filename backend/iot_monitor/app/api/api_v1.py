"""API v1 configuration."""

from fastapi import APIRouter

from app.api.routers import auth, roles, users
from app.iot_data.router import router as iot_router

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(roles.router)
api_router.include_router(users.router)
api_router.include_router(iot_router)
