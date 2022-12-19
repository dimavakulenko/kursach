import http
import uuid
from typing import Optional
import hashlib
import base64

import fastapi
from fastapi import APIRouter, Query, Path

from app.crud import create_user, get_verified_user, check_user_existence, get_list_orders, get_list_orders_by_customer_id
from app.utils.helpers import crypto_encode, crypto_decode, create_access_token, decode_access_token
from app.models.users import InformationAboutUser

router = fastapi.APIRouter(
    prefix='/customer',
    tags=['customer']
)


@router.post(
    "/",
)
async def customer_create(
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
                          photo_url, phone_number, country, city, 'customer')


@router.get(
    "/login"
)
async def customer_login(
        email: str = Query(...),
        password: str = Query(...),
):
    check_user_exist = await check_user_existence(crypto_encode(email),
                                                  crypto_encode(password), table='customers')
    jwt_token = create_access_token({"user_id": check_user_exist.id})
    return {"access_token": jwt_token, "token_type": "Bearer"}
