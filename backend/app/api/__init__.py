from fastapi import APIRouter
from app.api import kilns, bookings, firing_curves, artworks, uploads, auth

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(kilns.router)
api_router.include_router(bookings.router)
api_router.include_router(firing_curves.router)
api_router.include_router(artworks.router)
api_router.include_router(uploads.router)
