from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app.api import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="陶艺工作室窑位预约与烧制记录平台",
    description="独立陶艺工作室窑位预约、烧制曲线配置、作品生命周期追踪系统",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(api_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "陶艺工作室预约系统运行中"}
