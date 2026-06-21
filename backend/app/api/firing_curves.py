from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.services import FiringCurveService
from app.utils.auth import require_auth

router = APIRouter(prefix="/api/firing-curves", tags=["烧制曲线"])


@router.get("", response_model=List[schemas.FiringCurve])
def list_curves(
    clay_type: Optional[str] = Query(None, description="按泥料类型筛选"),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    return FiringCurveService.get_all(db, clay_type=clay_type)


@router.get("/{curve_id}", response_model=schemas.FiringCurve)
def get_curve(
    curve_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    curve = FiringCurveService.get_by_id(db, curve_id)
    if not curve:
        raise HTTPException(status_code=404, detail="曲线不存在")
    return curve


@router.get("/recommend/{clay_type}", response_model=Optional[schemas.FiringCurve])
def recommend_curve(
    clay_type: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    curve = FiringCurveService.get_default_for_clay(db, clay_type)
    if not curve:
        curves = FiringCurveService.get_all(db, clay_type=clay_type)
        if curves:
            return curves[0]
        return None
    return curve


@router.post("", response_model=schemas.FiringCurve, status_code=201)
def create_curve(
    data: schemas.FiringCurveCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    return FiringCurveService.create(db, data)


@router.put("/{curve_id}", response_model=schemas.FiringCurve)
def update_curve(
    curve_id: int,
    data: schemas.FiringCurveUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    curve = FiringCurveService.update(db, curve_id, data)
    if not curve:
        raise HTTPException(status_code=404, detail="曲线不存在")
    return curve


@router.delete("/{curve_id}")
def delete_curve(
    curve_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    if not FiringCurveService.delete(db, curve_id):
        raise HTTPException(status_code=404, detail="曲线不存在")
    return {"message": "删除成功"}
