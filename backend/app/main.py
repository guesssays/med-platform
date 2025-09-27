from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes_health import router as health_router
from app.api.v1.users import router as users_router
from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router

import app.db.base  # noqa: F401


app = FastAPI(title="Med Platform API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(health_router, prefix="/api/v1")
app.include_router(users_router,  prefix="/api/v1")
app.include_router(auth_router,   prefix="/api/v1")
app.include_router(admin_router,  prefix="/api/v1")
