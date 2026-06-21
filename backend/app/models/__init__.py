from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Kiln(Base):
    __tablename__ = "kilns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="窑炉名称")
    capacity = Column(String(100), comment="容量描述，如'0.5立方米'")
    max_temperature = Column(Float, comment="最高温度(℃)")
    status = Column(String(20), default="active", comment="状态: active/inactive/maintenance")
    description = Column(Text, comment="备注描述")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="kiln", cascade="all, delete-orphan")


class FiringCurve(Base):
    __tablename__ = "firing_curves"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="曲线名称")
    clay_type = Column(String(50), nullable=False, comment="适用泥料: 高白泥/紫砂/瓷泥/陶泥等")
    description = Column(Text, comment="曲线说明")
    stages = Column(JSON, nullable=False, comment="烧制阶段配置，包含升温/保温/降温参数")
    is_default = Column(Boolean, default=False, comment="是否为该泥料的默认曲线")
    created_by = Column(String(100), comment="创建人")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="firing_curve")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    kiln_id = Column(Integer, ForeignKey("kilns.id"), nullable=False)
    firing_curve_id = Column(Integer, ForeignKey("firing_curves.id"))
    title = Column(String(200), nullable=False, comment="预约标题")
    booker_name = Column(String(100), nullable=False, comment="预约人姓名")
    booker_contact = Column(String(100), comment="联系方式")
    start_time = Column(DateTime, nullable=False, comment="入窑时间")
    end_time = Column(DateTime, nullable=False, comment="出窑时间")
    status = Column(String(20), default="pending", comment="状态: pending/confirmed/in_progress/completed/cancelled")
    notes = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kiln = relationship("Kiln", back_populates="bookings")
    firing_curve = relationship("FiringCurve", back_populates="bookings")
    artworks = relationship("Artwork", back_populates="booking", cascade="all, delete-orphan")


class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    qr_code = Column(String(100), unique=True, index=True, nullable=False, comment="作品唯一识别码")
    title = Column(String(200), nullable=False, comment="作品名称")
    student_name = Column(String(100), nullable=False, comment="学员姓名")
    clay_type = Column(String(50), comment="泥料类型")
    description = Column(Text, comment="作品描述")
    current_stage = Column(String(50), default="drying", comment="当前阶段")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    booking = relationship("Booking", back_populates="artworks")
    stages = relationship("ArtworkStage", back_populates="artwork", cascade="all, delete-orphan", order_by="ArtworkStage.stage_order")


class ArtworkStage(Base):
    __tablename__ = "artwork_stages"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    stage_name = Column(String(50), nullable=False, comment="阶段名称")
    stage_key = Column(String(50), nullable=False, comment="阶段标识: drying/pre_heating/bisque_firing/glazing/ glaze_firing/cooling/completed")
    stage_order = Column(Integer, default=0, comment="阶段顺序")
    status = Column(String(20), default="pending", comment="状态: pending/in_progress/completed")
    temperature = Column(Float, comment="当前温度")
    notes = Column(Text, comment="阶段备注")
    photo_path = Column(String(500), comment="照片路径")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    operator = Column(String(100), comment="操作人")
    created_at = Column(DateTime, default=datetime.utcnow)

    artwork = relationship("Artwork", back_populates="stages")
