import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app import models
from app.config import settings
from app.utils import save_upload_file
from app.database import get_db
from app.utils.auth import require_auth

router = APIRouter(prefix="/api/uploads", tags=["文件上传"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@router.post("/artwork-photo")
async def upload_artwork_photo(
    file: UploadFile = File(...),
    _: models.User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}")

    file_data = await file.read()
    if len(file_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过10MB")

    file_path = save_upload_file(file_data, file.filename, "artworks")
    relative_path = os.path.relpath(file_path)

    return {
        "message": "上传成功",
        "file_path": relative_path,
        "filename": os.path.basename(file_path),
        "original_name": file.filename,
        "size": len(file_data)
    }


@router.get("/artwork-photo/{filename}")
async def get_artwork_photo(filename: str):
    file_path = os.path.join(settings.UPLOAD_DIR, "artworks", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    ext = os.path.splitext(filename)[1].lower()
    media_type = "image/jpeg"
    if ext == ".png":
        media_type = "image/png"
    elif ext == ".gif":
        media_type = "image/gif"
    elif ext == ".webp":
        media_type = "image/webp"
    return FileResponse(file_path, media_type=media_type)
