import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.chat import router as chat_router
from app.routers.meal_plan import router as meal_plan_router
from app.routers.vision import router as vision_router
from app.middleware.error_handler import register_handlers

# Configure logging
print("✅ 正在运行的是正确的 main.py 文件，时间戳: 2026-05-14")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

app = FastAPI(
    title="轻养AI API",
    description="轻养AI — AI 膳食康养后端服务",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat_router)
app.include_router(meal_plan_router)
app.include_router(vision_router)

# Global error handlers
register_handlers(app)


@app.get("/")
async def root():
    return {"service": "轻养AI API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
