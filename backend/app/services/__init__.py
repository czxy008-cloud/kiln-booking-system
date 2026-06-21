from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app import models, schemas
from app.utils import check_time_overlap, get_week_range


class KilnService:
    @staticmethod
    def get_all(db: Session, status: Optional[str] = None) -> List[models.Kiln]:
        query = db.query(models.Kiln)
        if status:
            query = query.filter(models.Kiln.status == status)
        return query.order_by(models.Kiln.id).all()

    @staticmethod
    def get_by_id(db: Session, kiln_id: int) -> Optional[models.Kiln]:
        return db.query(models.Kiln).filter(models.Kiln.id == kiln_id).first()

    @staticmethod
    def create(db: Session, data: schemas.KilnCreate) -> models.Kiln:
        kiln = models.Kiln(**data.model_dump())
        db.add(kiln)
        db.commit()
        db.refresh(kiln)
        return kiln

    @staticmethod
    def update(db: Session, kiln_id: int, data: schemas.KilnUpdate) -> Optional[models.Kiln]:
        kiln = KilnService.get_by_id(db, kiln_id)
        if not kiln:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(kiln, key, value)
        db.commit()
        db.refresh(kiln)
        return kiln

    @staticmethod
    def delete(db: Session, kiln_id: int) -> bool:
        kiln = KilnService.get_by_id(db, kiln_id)
        if not kiln:
            return False
        db.delete(kiln)
        db.commit()
        return True


class BookingService:
    @staticmethod
    def check_conflict(
        db: Session,
        kiln_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: Optional[int] = None,
    ) -> Tuple[bool, List[models.Booking]]:
        query = db.query(models.Booking).filter(
            models.Booking.kiln_id == kiln_id,
            models.Booking.status != "cancelled"
        )
        if exclude_booking_id:
            query = query.filter(models.Booking.id != exclude_booking_id)
        all_bookings = query.all()

        conflicts = []
        for booking in all_bookings:
            if check_time_overlap(start_time, end_time, booking.start_time, booking.end_time):
                conflicts.append(booking)
        return len(conflicts) > 0, conflicts

    @staticmethod
    def get_all(
        db: Session,
        kiln_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[List[str]] = None,
    ) -> List[models.Booking]:
        query = db.query(models.Booking)
        if kiln_id:
            query = query.filter(models.Booking.kiln_id == kiln_id)
        if status:
            query = query.filter(models.Booking.status.in_(status))
        if start_date:
            query = query.filter(models.Booking.end_time >= start_date)
        if end_date:
            query = query.filter(models.Booking.start_time <= end_date)
        return query.order_by(models.Booking.start_time).all()

    @staticmethod
    def get_week_bookings(db: Session, date: Optional[datetime] = None) -> dict:
        week_start, week_end = get_week_range(date)
        bookings = BookingService.get_all(db, start_date=week_start, end_date=week_end)

        result = {}
        kilns = KilnService.get_all(db)
        for kiln in kilns:
            result[kiln.id] = {
                "kiln": kiln,
                "bookings": [b for b in bookings if b.kiln_id == kiln.id]
            }
        return result

    @staticmethod
    def get_by_id(db: Session, booking_id: int) -> Optional[models.Booking]:
        return db.query(models.Booking).filter(models.Booking.id == booking_id).first()

    @staticmethod
    def create(db: Session, data: schemas.BookingCreate) -> models.Booking:
        booking = models.Booking(**data.model_dump())
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def update(db: Session, booking_id: int, data: schemas.BookingUpdate) -> Optional[models.Booking]:
        booking = BookingService.get_by_id(db, booking_id)
        if not booking:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(booking, key, value)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def delete(db: Session, booking_id: int) -> bool:
        booking = BookingService.get_by_id(db, booking_id)
        if not booking:
            return False
        db.delete(booking)
        db.commit()
        return True


class FiringCurveService:
    @staticmethod
    def get_all(db: Session, clay_type: Optional[str] = None) -> List[models.FiringCurve]:
        query = db.query(models.FiringCurve)
        if clay_type:
            query = query.filter(models.FiringCurve.clay_type == clay_type)
        return query.order_by(models.FiringCurve.id).all()

    @staticmethod
    def get_by_id(db: Session, curve_id: int) -> Optional[models.FiringCurve]:
        return db.query(models.FiringCurve).filter(models.FiringCurve.id == curve_id).first()

    @staticmethod
    def get_default_for_clay(db: Session, clay_type: str) -> Optional[models.FiringCurve]:
        return db.query(models.FiringCurve).filter(
            models.FiringCurve.clay_type == clay_type,
            models.FiringCurve.is_default == True
        ).first()

    @staticmethod
    def create(db: Session, data: schemas.FiringCurveCreate) -> models.FiringCurve:
        if data.is_default:
            db.query(models.FiringCurve).filter(
                models.FiringCurve.clay_type == data.clay_type
            ).update({"is_default": False})
        curve = models.FiringCurve(**data.model_dump())
        db.add(curve)
        db.commit()
        db.refresh(curve)
        return curve

    @staticmethod
    def update(db: Session, curve_id: int, data: schemas.FiringCurveUpdate) -> Optional[models.FiringCurve]:
        curve = FiringCurveService.get_by_id(db, curve_id)
        if not curve:
            return None
        update_data = data.model_dump(exclude_unset=True)
        if "is_default" in update_data and update_data["is_default"]:
            clay_type = update_data.get("clay_type") or curve.clay_type
            db.query(models.FiringCurve).filter(
                models.FiringCurve.clay_type == clay_type,
                models.FiringCurve.id != curve_id
            ).update({"is_default": False})
        for key, value in update_data.items():
            setattr(curve, key, value)
        db.commit()
        db.refresh(curve)
        return curve

    @staticmethod
    def delete(db: Session, curve_id: int) -> bool:
        curve = FiringCurveService.get_by_id(db, curve_id)
        if not curve:
            return False
        db.delete(curve)
        db.commit()
        return True


class ArtworkService:
    @staticmethod
    def get_all(
        db: Session,
        booking_id: Optional[int] = None,
        student_name: Optional[str] = None,
        current_stage: Optional[str] = None,
    ) -> List[models.Artwork]:
        query = db.query(models.Artwork)
        if booking_id:
            query = query.filter(models.Artwork.booking_id == booking_id)
        if student_name:
            query = query.filter(models.Artwork.student_name.like(f"%{student_name}%"))
        if current_stage:
            query = query.filter(models.Artwork.current_stage == current_stage)
        return query.order_by(models.Artwork.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, artwork_id: int) -> Optional[models.Artwork]:
        return db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()

    @staticmethod
    def get_by_qr(db: Session, qr_code: str) -> Optional[models.Artwork]:
        return db.query(models.Artwork).filter(models.Artwork.qr_code == qr_code).first()

    @staticmethod
    def create(db: Session, data: schemas.ArtworkCreate) -> models.Artwork:
        from app.utils import generate_qr_code, get_default_stages

        artwork = models.Artwork(**data.model_dump())
        artwork.qr_code = "TEMP"
        db.add(artwork)
        db.flush()
        artwork.qr_code = generate_qr_code(artwork.id)

        default_stages = get_default_stages()
        for idx, stage_data in enumerate(default_stages):
            stage = models.ArtworkStage(
                artwork_id=artwork.id,
                stage_name=stage_data["stage_name"],
                stage_key=stage_data["stage_key"],
                stage_order=stage_data["stage_order"],
                status="pending"
            )
            db.add(stage)
            if idx == 0:
                stage.status = "in_progress"
                stage.started_at = datetime.utcnow()

        db.commit()
        db.refresh(artwork)
        return artwork

    @staticmethod
    def update(db: Session, artwork_id: int, data: schemas.ArtworkUpdate) -> Optional[models.Artwork]:
        artwork = ArtworkService.get_by_id(db, artwork_id)
        if not artwork:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(artwork, key, value)
        db.commit()
        db.refresh(artwork)
        return artwork

    @staticmethod
    def delete(db: Session, artwork_id: int) -> bool:
        artwork = ArtworkService.get_by_id(db, artwork_id)
        if not artwork:
            return False
        db.delete(artwork)
        db.commit()
        return True

    @staticmethod
    def update_stage(db: Session, artwork_id: int, stage_key: str, data: schemas.ArtworkStageUpdate) -> Optional[models.ArtworkStage]:
        stage = db.query(models.ArtworkStage).filter(
            models.ArtworkStage.artwork_id == artwork_id,
            models.ArtworkStage.stage_key == stage_key
        ).first()
        if not stage:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(stage, key, value)
        db.commit()
        db.refresh(stage)

        artwork = ArtworkService.get_by_id(db, artwork_id)
        if artwork:
            completed_stages = [s for s in artwork.stages if s.status == "completed"]
            in_progress_stages = [s for s in artwork.stages if s.status == "in_progress"]
            if in_progress_stages:
                artwork.current_stage = in_progress_stages[0].stage_key
            elif completed_stages:
                artwork.current_stage = max(completed_stages, key=lambda s: s.stage_order).stage_key
            db.commit()

        return stage
