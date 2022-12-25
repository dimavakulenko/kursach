import http
import uuid
from typing import Optional
import hashlib
import base64
from fastapi import APIRouter, Query, Path, Body, Depends

from app.crud import create_user, get_verified_customer, check_user_existence, get_list_orders, \
    get_list_orders_by_customer_id, info_about_order, executor_done_orders, perform_executor_to_order, \
    update_order_executor_status
from app.utils.helpers import crypto_encode, crypto_decode, create_access_token, decode_access_token
from app.models.users import InformationAboutUser
from app.utils.token_decode import Token

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
    return {'status': 'ok'}


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
    return {"access_token": jwt_token,
            "token_type": "Bearer",
            "user": {
                'id': check_user_exist.id,
                'email': email,
                "name": crypto_decode(check_user_exist.name),
                "second_name": crypto_decode(check_user_exist.second_name),
                "photo_url": check_user_exist.photo_url,
                "phone_number": check_user_exist.phone_number,
                "country": check_user_exist.country,
                "city": check_user_exist.city,
            }
            }


@router.get(
    "/orders"
)
async def orders_list_by_type(
        type: Optional[str] = Query(default=None,description='order type(kompas,autocad,mathcad)')
):
    orders = await get_list_orders(type)
    return orders


@router.get(
    "/customer/{customer_id}",
)
async def get_customer(
        customer_id: uuid.UUID = Path(...)
):
    user_info = await get_verified_customer(customer_id)
    return user_info


@router.get(
    "/customer/{customer_id}/orders"
)
async def customer_orders(
        customer_id: uuid.UUID = Path(...)
):
    orders = await get_list_orders_by_customer_id(customer_id)
    return orders


@router.get(
    "/order/{order_id}"
)
async def get_order_info(
        order_id: uuid.UUID = Path()
):
    order_info = await info_about_order(order_id)
    return order_info


@router.get(
    "/order/done/"
)
async def list_executor_done_orders(
        token: Token = Depends()
):
    executor_id = token.token_data['user_id']
    done_orders_info = await executor_done_orders(executor_id)
    return done_orders_info


@router.get(
    "/order/in_progress/"
)
async def list_executor_in_progress_orders(
        token: Token = Depends()
):
    executor_id = token.token_data['user_id']
    progress_orders_info = await executor_done_orders(executor_id)
    return progress_orders_info


@router.post(
    "/order/{order_id}/performed"
)
async def perform_executor(
        token: Token = Depends(),
        order_id: uuid.UUID = Path(),
):
    executor_id = token.token_data['user_id']
    perform = await perform_executor_to_order(executor_id, order_id)
    return {'status': 'ok'}


@router.post(
    "/order/{order_id}/status/update"
)
async def change_executor_status(
        token: Token = Depends(),
        order_id: uuid.UUID = Path(),
        status: str = Body(example='progress/done/review/search')
):
    executor_id = token.token_data['user_id']
    status_update = await update_order_executor_status(order_id, status, executor_id)
    return {'status': 'ok'}
