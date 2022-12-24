import datetime
import hashlib
from http import HTTPStatus
import uuid
from typing import Optional

import asyncpg.exceptions
from fastapi import HTTPException

from app.database import database
from app.models.database import executor, Executor
from app.utils.helpers import crypto_decode, crypto_encode


async def check_email_existence(
        email: bytes,
        role: str
):
    query = '''SELECT FROM public.{} WHERE email = :email'''.format('customers' if role == 'customer' else 'executors')
    email_check = await database.fetch_one(query=query,
                                           values={
                                               'email': email.decode('utf-8'),
                                           }
                                           )
    return email_check


async def check_user_existence(
        email: bytes,
        password: bytes,
        table: str
):
    query = '''SELECT * FROM public.{} WHERE email = :email and password = :password'''.format(table)
    user_check = await database.fetch_one(query=query,
                                          values={
                                              'email': email.decode('utf-8'),
                                              'password': password.decode('utf-8'),
                                          }
                                          )
    if user_check is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='user does not exist')
    return user_check


async def get_list_orders(
        type: str
):
    query = '''select title, price, date from orders where type_id =(select id from order_types where name = :type) 
    order by date desc '''
    orders = await database.fetch_all(query=query,
                                      values={
                                          'type': type,
                                      }
                                      )
    return orders


async def get_list_orders_by_customer_id(
        customer_id: uuid.UUID
):
    query = '''select title, price, date from orders where customer_id =:customer_id
    order by date desc '''
    orders = await database.fetch_one(query=query,
                                      values={
                                          'customer_id': customer_id,
                                      }
                                      )
    return orders


async def get_role_id(
        role: str
):
    query = '''SELECT id FROM public.roles where name ilike :role'''
    role_id = await database.fetch_one(query=query,
                                       values={
                                           'role': role
                                       }
                                       )
    return role_id.id


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
        role: str,
):
    email_check = await check_email_existence(email, role)
    if email_check is not None:
        raise HTTPException(HTTPStatus.CONFLICT, detail='user already exist')
    role_id = await get_role_id(role=role)
    query = '''INSERT INTO public.{} (id,email,password,name,second_name,birth_date,photo_url,phone_number,
    country,city,role_id)
    values (:id,:email,:password,:name,:second_name,TO_DATE(:birth_date,'DD.MM.YYYY'),:photo_url,:phone_number,
    :country,:city, :role_id)'''.format('customers' if role == 'customer' else 'executors')
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
                                                'role_id': role_id,
                                            }
                                            )


async def get_verified_customer(id: uuid.UUID):
    query = '''select * from public.customers where id=:id'''
    customer_info = await database.fetch_one(query, values={'id': id})
    if customer_info is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        'name': customer_info.name,
        'second_name': customer_info.second_name,
        'photo_url': customer_info.photo_url,
        'country': customer_info.country,
    }


async def get_verified_executor(id: uuid.UUID):
    query = '''select  avg(r.rating) as rating, name,second_name,photo_url,phone_number,country from public.executors
    left join public.reviews r on r.executor_id = :id
    where executors.id= :id
    GROUP BY name,second_name,photo_url,phone_number,country'''
    executor_info = await database.fetch_one(query, values={'id': id})
    if executor_info is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        'name': crypto_decode(executor_info.name),
        'second_name': crypto_decode(executor_info.second_name),
        'photo_url': executor_info.photo_url,
        'phone_number': executor_info.phone_number,
        'country': executor_info.country,
        'rating': executor_info.rating
    }


async def create_order(customer_id: str, title: str, description: str, files: str, price: float, type: str):
    query = '''SELECT id FROM order_types where name ilike :type'''
    type_id = await database.fetch_one(query, values={'type': type})
    if type_id is None:
        raise HTTPException(status_code=404, detail="This order type does not exist")
    query = '''INSERT INTO orders (id, customer_id, title, description, files, price, type_id, date) 
    values (:id, :customer_id, :title, :description, :files, :price, :type_id, :date)'''
    try:
        order_create = await database.fetch_one(query, values={'id': uuid.uuid4(),
                                                               'customer_id': customer_id,
                                                               'title': title,
                                                               'description': description,
                                                               'files': files,
                                                               'price': str(price),
                                                               'type_id': type_id.id,
                                                               'date': datetime.datetime.today()
                                                               })
    except asyncpg.exceptions.DataError:
        raise HTTPException(status_code=422, detail='Wrong order parameters type')


async def update_order(order_id: uuid.UUID, customer_id: uuid.UUID, title: str,
                       description: str, files: str, price: float, type: str):
    query = '''SELECT * FROM orders where id=:id and customer_id=:customer_id'''
    order_existance = await database.fetch_one(query, values={'id': order_id,
                                                              'customer_id': customer_id})
    if order_existance is None:
        raise HTTPException(status_code=404, detail="This order does not exist")
    query = '''SELECT id FROM order_types where name ilike :type'''
    type_id = await database.fetch_one(query, values={'type': type})
    if type_id is None:
        raise HTTPException(status_code=404, detail="This order type does not exist")
    query = '''UPDATE orders SET title=:title, description = :description, files =:files, price=:price, 
                                                        type_id=:type_id where id=:id'''
    try:
        order_update = await database.fetch_one(query, values={'id': order_id,
                                                               'title': title,
                                                               'description': description,
                                                               'files': files,
                                                               'price': str(price),
                                                               'type_id': type_id.id,
                                                               })
    except asyncpg.exceptions.DataError:
        raise HTTPException(status_code=422, detail='Wrong order parameters type')


async def delete_order(order_id, customer_id):
    query = '''DELETE from orders where id=:order_id and customer_id=:customer_id'''
    _ = await database.fetch_one(query, values={'order_id': order_id,
                                                'customer_id': customer_id})


async def executor_review(customer_id, executor_id, text, rating):
    query = '''INSERT INTO public.reviews (id, customer_id, executor_id, text, rating) 
    values (:id, :customer_id, :executor_id, :text, :rating)'''
    _ = await database.fetch_one(query, values={'id': uuid.uuid4(),
                                                'customer_id': customer_id,
                                                'executor_id': executor_id,
                                                'text': text,
                                                'rating': rating
                                                }
                                 )


async def executor_approve(order_id):
    query = '''UPDATE comments SET confirmed = True where order_id = :order_id'''
    _ = await database.fetch_one(query,
                                 values={
                                     'order_id': order_id,
                                 }
                                 )


async def executor_reject(order_id):
    query = '''UPDATE comments SET confirmed = False where order_id = :order_id'''
    _ = await database.fetch_one(query,
                                 values={
                                     'order_id': order_id,
                                 }
                                 )


async def order_status_customer(order_id):
    query = '''SELECT name FROM public.status where id = (SELECT deal_status_customer FROM deals where 
    comment_id=(select id from public.comments where order_id = :order_id))'''
    order_status = await database.fetch_one(query,
                                            values={
                                                'order_id': order_id,
                                            }
                                            )
    return order_status.name


async def orders_list(customer_id):
    query = '''SELECT title, price, date from public.orders where customer_id = :customer_id ORDER BY date desc'''
    orders_info = await database.fetch_all(query,
                                           values={
                                               'customer_id': customer_id,
                                           }
                                           )
    if orders_info is None:
        raise HTTPException(status_code=404, detail="This user doesn't have orders")
    return orders_info


async def get_list_executors():
    query = '''select  avg(r.rating) as rating, name,second_name,photo_url,phone_number,country from public.executors
    left join public.reviews r on r.executor_id = public.executors.id
    GROUP BY name,second_name,photo_url,phone_number,country'''
    executors_info = await database.fetch_all(query)
    return [{
        'name': crypto_decode(i.name),
        'second_name': crypto_decode(i.second_name),
        'photo_url': i.photo_url,
        'phone_number': i.phone_number,
        'country': i.country,
        'rating': i.rating
    } for i in executors_info]

# async def get_executor(executor_id: uuid.UUID):
#     query = '''select * from public.executors where id=:id'''
#     customer_info = await database.fetch_one(query, values={'id': id})
#     if customer_info is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {
#         'name': customer_info.name,
#         'second_name': customer_info.second_name,
#         'photo_url': customer_info.photo_url,
#         'country': customer_info.country,
#     }
