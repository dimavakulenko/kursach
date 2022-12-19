import datetime
import hashlib
from http import HTTPStatus
import uuid
from typing import Optional

from fastapi import HTTPException

from app.database import database
from app.models.database import executor, Executor


async def check_email_existence(
        email: bytes
):
    query = '''SELECT FROM public.executors WHERE email = :email'''
    email_check = await database.fetch_one(query=query,
                                           values={
                                               'email': email.decode('utf-8'),
                                           }
                                           )
    return email_check


async def check_user_existence(
        email: bytes,
        password: bytes
):
    query = '''SELECT FROM public.executors WHERE email = :email and password = :password'''
    user_check = await database.fetch_one(query=query,
                                           values={
                                               'email': email.decode('utf-8'),
                                               'password': password.decode('utf-8'),
                                           }
                                           )
    if user_check is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='user does not exist')
    return user_check


async def create_user(
        email: bytes,
        password: bytes,
        name: bytes,
        second_name: bytes,
        birth_date: str,
        photo_url: str,
        phone_number: str,
        country: str,
        city: str,
):
    email_check = await check_email_existence(email)
    if email_check is not None:
        raise HTTPException(HTTPStatus.CONFLICT, detail='user already exist')
    query = '''INSERT INTO public.executors (id,email,password,name,second_name,birth_date,photo_url,phone_number,
    country,city,role_id)
    values (:id,:email,:password,:name,:second_name,TO_DATE(:birth_date,'DDMMYYYY'),:photo_url,:phone_number,
    :country,:city, :role_id)'''
    add_new_user = await database.fetch_one(query=query,
                                            values={
                                                'id': uuid.uuid4(),
                                                'email': email.decode('utf-8'),
                                                'password': password.decode('utf-8'),
                                                'name': name.decode('utf-8'),
                                                'second_name': second_name.decode('utf-8'),
                                                'birth_date': birth_date,
                                                'photo_url': photo_url,
                                                'phone_number': phone_number,
                                                'country': country,
                                                'city': city,
                                                'role_id': 'cdfa1315-68e9-4ff9-b3f9-f5ff38a2bdca',
                                            }
                                            )


async def get_verified_user(id: int):
    query = '''select * from public.users where id=:id'''
    user_info = await database.fetch_one(query, values={'id': id})
    if user_info is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        'name': user_info.name,
        'second_name': user_info.second_name,
        'photo_url': user_info.photo_url,
        'country': user_info.country,
    }
