import http
import uuid
from typing import Optional
import hashlib
import base64

import fastapi
from fastapi import APIRouter, Query, Path, Depends

from app.crud import create_user, get_verified_executor, check_user_existence, \
    get_list_orders, get_list_orders_by_customer_id, create_order, update_order,order_delete
from app.utils.helpers import crypto_encode, crypto_decode, create_access_token, decode_access_token
from app.models.users import InformationAboutUser
from app.utils.token_decode import Token

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
    jwt_token = create_access_token({"user_id": str(check_user_exist.id)})
    return {"access_token": jwt_token, "token_type": "Bearer"}


@router.get(
    "/executor/{executor_id}"
)
async def executor_info(
        executor_id: uuid.UUID = Path(...)
):
    customer_info = await get_verified_executor(executor_id)
    return customer_info


@router.post(
    "/order"
)
async def order_create(
        user_id: str = Query(...),
        title: str = Query(max_length=50),
        description: str = Query(max_length=300),
        files: str = Query(description='file links'),
        price: float = Query(...),
        type: str = Query(max_length=20),
        token: Token = Depends()
):
    customer_id = token.token_data['user_id']
    _ = await create_order(customer_id, title, description, files, price, type)
    a = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjpudWxsLCJleHAiOjE2NzE4MjU0MDF9.RDH_xsKGXIj37gajO8X-IViLvEUmO2yxymJqR58sWV8'


@router.post(
    "/order/update"
)
async def order_update(
        order_id: uuid.UUID = Query(...),
        title: str = Query(max_length=50),
        description: str = Query(max_length=300),
        files: str = Query(description='file links'),
        price: float = Query(...),
        type: str = Query(...)
):
    _ = await update_order(order_id, title, description, files, price, type)


@router.delete(
    "/order/{order_id}/delete"
)
async def order_delete(
        order_id: uuid.UUID = Path(...),
):
    _ = await order_delete(order_id)