"""Configuración del API v1."""

from fastapi import APIRouter

from app.api.routers import roles, users

api_router = APIRouter()
api_router.include_router(roles.router)
api_router.include_router(users.router)
