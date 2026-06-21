from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.services import KilnService
from app.utils.auth import require_auth

router = APIRouter(prefix="/api/kilns", tags=["窑炉管理"])


@router.get("", response_model=List[schemas.Kiln])
def list_kilns(
    status: Optional[str] = Query(None, description="筛选状态: active/inactive/maintenance"),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    return KilnService.get_all(db, status=status)


@router.get("/{kiln_id}", response_model=schemas.Kiln)
def get_kiln(
    kiln_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    kiln = KilnService.get_by_id(db, kiln_id)
    if not kiln:
        raise HTTPException(status_code=404, detail="窑炉不存在")
    return kiln


@router.post("", response_model=schemas.Kiln, status_code=201)
def create_kiln(
    data: schemas.KilnCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    return KilnService.create(db, data)


@router.put("/{kiln_id}", response_model=schemas.Kiln)
def update_kiln(
    kiln_id: int,
    data: schemas.KilnUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    kiln = KilnService.update(db, kiln_id, data)
    if not kiln:
        raise HTTPException(status_code=404, detail="窑炉不存在")
    return kiln


@router.delete("/{kiln_id}")
def delete_kiln(
    kiln_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    if not KilnService.delete(db, kiln_id):
        raise HTTPException(status_code=404, detail="窑炉不存在")
    return {"message": "删除成功"}
