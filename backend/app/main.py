# app/main.py
from fastapi import FastAPI
from app.api.v1.routes_health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router

import app.db.base  # noqa: F401  импорт моделей

app = FastAPI(title="Med Platform API")

# Единый префикс API
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router,   prefix="/api/v1")
app.include_router(users_router,  prefix="/api/v1")
