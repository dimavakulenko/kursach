import http
import uuid
from typing import Optional
import hashlib
import base64

import fastapi
from fastapi import APIRouter, Query, Path, Depends, Body

from app.crud import create_user, get_verified_executor, check_user_existence, \
    get_list_orders, get_list_orders_by_customer_id, create_order, update_order, delete_order, executor_review, \
    executor_approve, executor_reject, order_status_customer, orders_list, get_list_executors, info_about_order,\
    update_order_customer_status
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
        email: str = Body(...),
        password: str = Body(...),
        name: str = Body(...),
        second_name: str = Body(...),
        birth_date: str = Body(...),
        photo_url: Optional[str] = Body(default=None),
        phone_number: str = Body(...),
        country: Optional[str] = Body(...),
        city: Optional[str] = Body(...),
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
        title: str = Body(max_length=50),
        description: str = Body(max_length=300),
        files: str = Body(description='file links'),
        price: float = Body(...),
        type: str = Body(max_length=20),
        token: Token = Depends()
):
    customer_id = token.token_data['user_id']
    _ = await create_order(customer_id, title, description, files, price, type)


@router.post(
    "/order/update"
)
async def order_update(
        order_id: uuid.UUID = Body(...),
        title: str = Body(max_length=50),
        description: str = Body(max_length=300),
        files: str = Body(description='file links'),
        price: float = Body(...),
        type: str = Body(...),
        token: Token = Depends()
):
    customer_id = token.token_data['user_id']
    _ = await update_order(order_id, customer_id, title, description, files, price, type)


@router.delete(
    "/order/{order_id}/delete"
)
async def order_delete(
        order_id: uuid.UUID = Path(...),
        token: Token = Depends()
):
    customer_id = token.token_data['user_id']
    _ = await delete_order(order_id, customer_id)


@router.post(
    "/order/{order_id}/approve"
)
async def approve_executor(
        order_id: uuid.UUID = Path(),
        executor_id: uuid.UUID = Query(...)
):
    _ = await executor_approve(order_id, executor_id)


@router.post(
    "/order/{order_id}/reject"
)
async def reject_executor(
        order_id: uuid.UUID = Path(),
        executor_id: uuid.UUID = Query(...)
):
    _ = await executor_reject(order_id, executor_id)


@router.post(
    "/order/{order_id}/review"
)
async def review_executor(
        executor_id: uuid.UUID = Body(...),
        text: str = Body(...),
        rating: float = Body(...),
        token: Token = Depends()
):
    customer_id = token.token_data['user_id']
    _ = await executor_review(customer_id, executor_id, text, rating)


@router.get(
    "/order/{order_id}/status"
)
async def get_status(
        order_id: uuid.UUID = Path(...),
):
    order_status = await order_status_customer(order_id)
    return {'status': order_status}


@router.get(
    "/order/list"
)
async def list_of_orders(
        token: Token = Depends()
):
    customer_id = token.token_data['user_id']
    orders = await orders_list(customer_id)
    return [
        {
            'id': i.id,
            'title': i.title,
            'price': i.price,
            'date': i.date,
        } for i in orders
    ]


@router.get(
    "/executors/list"
)
async def executors_list():
    customer_info = await get_list_executors()
    return customer_info


@router.get(
    "/order/{order_id}"
)
async def order_info(
    order_id: uuid.UUID = Path(),
):
    info_order = await info_about_order(order_id)
    return info_order


@router.post(
    "/order/{order_id}/status/update"
)
async def update_status(
    order_id: uuid.UUID = Path(),
    token: Token = Depends(),
    status: str = Body(example='progress/done/review/search')
):
    customer_id = token.token_data['user_id']
    status_update = await update_order_customer_status(order_id,status, customer_id)
