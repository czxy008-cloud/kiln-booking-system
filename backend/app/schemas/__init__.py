from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = "user"


class UserCreate(UserBase):
    password: str = Field(..., min_length=4)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "User"


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: Optional[str] = None


class KilnBase(BaseModel):
    name: str = Field(..., max_length=100)
    capacity: Optional[str] = None
    max_temperature: Optional[float] = None
    status: Optional[str] = "active"
    description: Optional[str] = None


class KilnCreate(KilnBase):
    pass


class KilnUpdate(KilnBase):
    name: Optional[str] = None


class Kiln(KilnBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FiringStage(BaseModel):
    name: str
    stage_type: str = Field(..., description="heating/holding/cooling")
    start_temp: float
    end_temp: float
    duration_minutes: int
    rate: Optional[float] = Field(None, description="升温速率℃/h")
    notes: Optional[str] = None


class FiringCurveBase(BaseModel):
    name: str = Field(..., max_length=100)
    clay_type: str = Field(..., max_length=50)
    description: Optional[str] = None
    stages: List[FiringStage]
    is_default: Optional[bool] = False
    created_by: Optional[str] = None


class FiringCurveCreate(FiringCurveBase):
    pass


class FiringCurveUpdate(BaseModel):
    name: Optional[str] = None
    clay_type: Optional[str] = None
    description: Optional[str] = None
    stages: Optional[List[FiringStage]] = None
    is_default: Optional[bool] = None


class FiringCurve(FiringCurveBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    kiln_id: int
    firing_curve_id: Optional[int] = None
    title: str = Field(..., max_length=200)
    booker_name: str = Field(..., max_length=100)
    booker_contact: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: Optional[str] = "pending"
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    kiln_id: Optional[int] = None
    firing_curve_id: Optional[int] = None
    title: Optional[str] = None
    booker_name: Optional[str] = None
    booker_contact: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Booking(BookingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    kiln: Optional[Kiln] = None
    firing_curve: Optional[FiringCurve] = None

    class Config:
        from_attributes = True


class BookingWithArtworks(Booking):
    artworks: List["Artwork"] = []


class ConflictCheckResult(BaseModel):
    has_conflict: bool
    conflicting_bookings: List[Booking] = []


class ArtworkStageBase(BaseModel):
    stage_name: str
    stage_key: str
    stage_order: Optional[int] = 0
    status: Optional[str] = "pending"
    temperature: Optional[float] = None
    notes: Optional[str] = None
    photo_path: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    operator: Optional[str] = None


class ArtworkStageCreate(ArtworkStageBase):
    pass


class ArtworkStageUpdate(BaseModel):
    stage_name: Optional[str] = None
    status: Optional[str] = None
    temperature: Optional[float] = None
    notes: Optional[str] = None
    photo_path: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    operator: Optional[str] = None


class ArtworkStage(ArtworkStageBase):
    id: int
    artwork_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ArtworkBase(BaseModel):
    booking_id: Optional[int] = None
    title: str = Field(..., max_length=200)
    student_name: str = Field(..., max_length=100)
    clay_type: Optional[str] = None
    description: Optional[str] = None
    current_stage: Optional[str] = "drying"


class ArtworkCreate(ArtworkBase):
    pass


class ArtworkUpdate(BaseModel):
    booking_id: Optional[int] = None
    title: Optional[str] = None
    student_name: Optional[str] = None
    clay_type: Optional[str] = None
    description: Optional[str] = None
    current_stage: Optional[str] = None


class Artwork(ArtworkBase):
    id: int
    qr_code: str
    created_at: datetime
    updated_at: datetime
    stages: List[ArtworkStage] = []

    class Config:
        from_attributes = True


Token.model_rebuild()
BookingWithArtworks.model_rebuild()
