import uuid
import io
import os
from datetime import datetime, timedelta
from typing import List, Optional
import qrcode
from app.config import settings


def generate_qr_code(artwork_id: int) -> str:
    unique_code = f"KW-{artwork_id}-{uuid.uuid4().hex[:8].upper()}"
    return unique_code


def get_qr_base_url(custom_base: Optional[str] = None) -> str:
    if custom_base:
        return custom_base.rstrip('/')
    if settings.QR_CODE_BASE_URL:
        return settings.QR_CODE_BASE_URL.rstrip('/')
    return settings.FRONTEND_BASE_URL.rstrip('/')


def generate_qr_image(
    qr_code: str,
    save_path: Optional[str] = None,
    as_url: bool = True,
    base_url: Optional[str] = None
) -> bytes:
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    if as_url:
        base = get_qr_base_url(base_url)
        qr_data = f"{base}/artworks/{qr_code}"
    else:
        qr_data = qr_code
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#5d4e37", back_color="#faf6f0")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def get_week_range(date: Optional[datetime] = None) -> tuple:
    if date is None:
        date = datetime.now()
    start = date - timedelta(days=date.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    return start, end


def check_time_overlap(
    start1: datetime, end1: datetime, start2: datetime, end2: datetime
) -> bool:
    return start1 < end2 and start2 < end1


def get_default_stages() -> List[dict]:
    return [
        {"stage_name": "入窑前干燥", "stage_key": "drying", "stage_order": 1},
        {"stage_name": "预热阶段", "stage_key": "pre_heating", "stage_order": 2},
        {"stage_name": "素烧阶段", "stage_key": "bisque_firing", "stage_order": 3},
        {"stage_name": "施釉阶段", "stage_key": "glazing", "stage_order": 4},
        {"stage_name": "釉烧阶段", "stage_key": "glaze_firing", "stage_order": 5},
        {"stage_name": "出窑冷却", "stage_key": "cooling", "stage_order": 6},
        {"stage_name": "烧制完成", "stage_key": "completed", "stage_order": 7},
    ]


def save_upload_file(file_data: bytes, filename: str, subfolder: str = "artworks") -> str:
    upload_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(filename)[1] or ".jpg"
    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(upload_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(file_data)

    return file_path
