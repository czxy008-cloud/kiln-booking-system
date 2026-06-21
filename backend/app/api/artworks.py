from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.services import ArtworkService
from app.utils import generate_qr_image
from app.utils.auth import require_auth

router = APIRouter(prefix="/api/artworks", tags=["作品管理"])


@router.get("", response_model=List[schemas.Artwork])
def list_artworks(
    booking_id: Optional[int] = Query(None),
    student_name: Optional[str] = Query(None),
    current_stage: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return ArtworkService.get_all(db, booking_id=booking_id, student_name=student_name, current_stage=current_stage)


@router.get("/by-qr/{qr_code}", response_model=schemas.Artwork)
def get_artwork_by_qr(qr_code: str, db: Session = Depends(get_db)):
    artwork = ArtworkService.get_by_qr(db, qr_code)
    if not artwork:
        raise HTTPException(status_code=404, detail="作品不存在，请检查二维码")
    return artwork


@router.get("/{artwork_id}", response_model=schemas.Artwork)
def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    artwork = ArtworkService.get_by_id(db, artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="作品不存在")
    return artwork


@router.get("/{artwork_id}/qrcode")
def get_artwork_qrcode(artwork_id: int, db: Session = Depends(get_db)):
    artwork = ArtworkService.get_by_id(db, artwork_id)
    if not artwork:
        raise HTTPException(status_code=404, detail="作品不存在")
    img_bytes = generate_qr_image(artwork.qr_code)
    return Response(content=img_bytes, media_type="image/png")


@router.post("", response_model=schemas.Artwork, status_code=201)
def create_artwork(
    data: schemas.ArtworkCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    return ArtworkService.create(db, data)


@router.put("/{artwork_id}", response_model=schemas.Artwork)
def update_artwork(
    artwork_id: int,
    data: schemas.ArtworkUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    artwork = ArtworkService.update(db, artwork_id, data)
    if not artwork:
        raise HTTPException(status_code=404, detail="作品不存在")
    return artwork


@router.delete("/{artwork_id}")
def delete_artwork(
    artwork_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    if not ArtworkService.delete(db, artwork_id):
        raise HTTPException(status_code=404, detail="作品不存在")
    return {"message": "删除成功"}


@router.put("/{artwork_id}/stages/{stage_key}", response_model=schemas.ArtworkStage)
def update_artwork_stage(
    artwork_id: int,
    stage_key: str,
    data: schemas.ArtworkStageUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    stage = ArtworkService.update_stage(db, artwork_id, stage_key, data)
    if not stage:
        raise HTTPException(status_code=404, detail="阶段不存在")
    return stage
