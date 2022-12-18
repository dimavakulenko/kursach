import http
from typing import Optional
import hashlib
import base64
from fastapi import APIRouter, Query, Path

from app.crud import create_user, get_verified_user
from app.utils.helpers import crypto_encode, user_information_decoder
from app.models.users import InformationAboutUser

router = APIRouter(
    tags=["executor"]
)


@router.post(
    "/executor",
)
async def user_create(
        email: str = Query(...),
        password: str = Query(...),
        name: str = Query(...),
        second_name: str = Query(...),
        birth_date: str = Query(...),
        photo_url: Optional[str] = Query(default=None),
        phone_number: str = Query(...),
        country: Optional[str] = Query(...),
        city: Optional[str] = Query(...),
):
    _ = await create_user(crypto_encode(email), crypto_encode(password),
                          crypto_encode(name), crypto_encode(second_name), birth_date,
                          photo_url, phone_number, country, city)


@router.get(
    "/executor/login"
)
async def executor_login(
        email: str = Query(...),
        password: str = Query(...),
):
    pass


@router.get(
    "/executor/{id}",
    response_model=InformationAboutUser
)
async def get_executor(
        id: int = Path(...)
):
    user_info = await get_verified_user(id)
    return {
        'name': user_information_decoder(user_info['name'].encode('utf-8')),
        'second_name': user_information_decoder(user_info['second_name'].encode('utf-8')),
        'photo_url': user_info['photo_url'],
        'country': user_info['country'],
    }
