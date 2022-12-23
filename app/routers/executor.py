import http
import uuid
from typing import Optional
import hashlib
import base64
from fastapi import APIRouter, Query, Path

from app.crud import create_user, get_verified_customer, check_user_existence, get_list_orders, get_list_orders_by_customer_id
from app.utils.helpers import crypto_encode, crypto_decode, create_access_token, decode_access_token
from app.models.users import InformationAboutUser

router = APIRouter(
    tags=["executor"],
    prefix='/executor'
)


@router.post(
    "/",
)
async def executor_create(
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
                          photo_url, phone_number, country, city, 'executor')


@router.get(
    "/login"
)
async def executor_login(
        email: str = Query(...),
        password: str = Query(...),
):
    check_user_exist = await check_user_existence(crypto_encode(email),
                                                  crypto_encode(password), table='executors')
    jwt_token = create_access_token({"user_id": str(check_user_exist.id)})
    return {"access_token": jwt_token, "token_type": "Bearer"}


@router.get(
    "/orders"
)
async def orders_list(
        type: str = Query(..., description='order type(Kompas,Autocad,Mathcad)')
):
    orders = get_list_orders(type)
    result = [
        {
            'title': i['title'],
            'price': i['price'],
            'date': i['date'],
        } for i in orders
    ]
    return result


@router.get(
    "/customer/{customer_id}",
    response_model=InformationAboutUser
)
async def get_customer(
        customer_id: uuid.UUID = Path(...)
):
    user_info = await get_verified_user(customer_id)
    return {
        'name': crypto_decode(user_info['name'].encode('utf-8')),
        'second_name': crypto_decode(user_info['second_name'].encode('utf-8')),
        'photo_url': user_info['photo_url'],
        'country': user_info['country'],
        'phone_number': user_info['phone_number']
    }


@router.get(
    "/customer/{customer_id}/orders:"
)
async def orders_list(
        type: str = Query(..., description='order type(Kompas,Autocad,Mathcad)')
):
    orders = get_list_orders_by_customer_id(type)
    result = [
        {
            'title': i['title'],
            'price': i['price'],
            'date': i['date'],
        } for i in orders
    ]
    return result
