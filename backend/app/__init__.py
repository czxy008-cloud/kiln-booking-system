import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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


FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "frontend", "dist")
FRONTEND_INDEX = os.path.abspath(os.path.join(FRONTEND_DIST, "index.html"))

if os.path.exists(FRONTEND_INDEX):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="frontend-assets")

    @app.get("/{full_path:path}")
    async def spa_catch_all(request: Request, full_path: str):
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        if os.path.exists(FRONTEND_INDEX):
            return FileResponse(FRONTEND_INDEX)
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Frontend not built")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "陶艺工作室预约系统运行中"}
