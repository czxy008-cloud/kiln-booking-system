from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.services import BookingService
from app.utils.auth import require_auth

router = APIRouter(prefix="/api/bookings", tags=["预约管理"])


@router.get("", response_model=List[schemas.Booking])
def list_bookings(
    kiln_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    return BookingService.get_all(db, kiln_id=kiln_id, start_date=start_date, end_date=end_date, status=status)


@router.get("/week", response_model=dict)
def get_week_calendar(
    date: Optional[datetime] = Query(None, description="基准日期，默认今天"),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    data = BookingService.get_week_bookings(db, date)
    result = {}
    for kiln_id, item in data.items():
        result[str(kiln_id)] = {
            "kiln": schemas.Kiln.model_validate(item["kiln"]).model_dump(),
            "bookings": [schemas.Booking.model_validate(b).model_dump() for b in item["bookings"]]
        }
    return result


@router.get("/check-conflict", response_model=schemas.ConflictCheckResult)
def check_conflict(
    kiln_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    has_conflict, conflicts = BookingService.check_conflict(db, kiln_id, start_time, end_time, exclude_booking_id)
    return {
        "has_conflict": has_conflict,
        "conflicting_bookings": [schemas.Booking.model_validate(b) for b in conflicts]
    }


@router.get("/{booking_id}", response_model=schemas.BookingWithArtworks)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    booking = BookingService.get_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    return booking


@router.post("", response_model=schemas.Booking, status_code=201)
def create_booking(
    data: schemas.BookingCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    has_conflict, conflicts = BookingService.check_conflict(db, data.kiln_id, data.start_time, data.end_time)
    if has_conflict:
        conflict_info = [f"{b.title} ({b.start_time} ~ {b.end_time})" for b in conflicts]
        raise HTTPException(
            status_code=409,
            detail=f"时间冲突！以下预约与此时间段重叠：{'; '.join(conflict_info)}"
        )
    return BookingService.create(db, data)


@router.put("/{booking_id}", response_model=schemas.Booking)
def update_booking(
    booking_id: int,
    data: schemas.BookingUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    booking = BookingService.get_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")

    kiln_id = data.kiln_id if data.kiln_id is not None else booking.kiln_id
    start_time = data.start_time if data.start_time is not None else booking.start_time
    end_time = data.end_time if data.end_time is not None else booking.end_time

    if data.kiln_id is not None or data.start_time is not None or data.end_time is not None:
        has_conflict, conflicts = BookingService.check_conflict(db, kiln_id, start_time, end_time, booking_id)
        if has_conflict:
            conflict_info = [f"{b.title} ({b.start_time} ~ {b.end_time})" for b in conflicts]
            raise HTTPException(
                status_code=409,
                detail=f"时间冲突！以下预约与此时间段重叠：{'; '.join(conflict_info)}"
            )

    return BookingService.update(db, booking_id, data)


@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_auth)
):
    if not BookingService.delete(db, booking_id):
        raise HTTPException(status_code=404, detail="预约不存在")
    return {"message": "删除成功"}
