import datetime
import hashlib
# import urllib.parse
import urllib
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
    if type:
        query = '''select ord.id, title, price,ot.name as type, date from orders ord
            join order_types ot on ord.type_id = ot.id
        where type_id =(select id from order_types where name = :type) 
        order by date desc '''
        orders = await database.fetch_all(query=query,
                                          values={
                                              'type': type,
                                          }
                                          )
    else:
        query = '''select ord.id, title, price,ot.name as type, date from orders ord
                join order_types ot on ord.type_id = ot.id
                order by date desc '''
        orders = await database.fetch_all(query=query)
    return [
        {
            'id': i.id,
            'title': i.title,
            'price': i.price,
            'date': i.date,
            'type': i.type
        } for i in orders
    ]


async def get_list_orders_by_customer_id(
        customer_id: uuid.UUID
):
    query = '''select id, title, price, date from orders where customer_id =:customer_id
    order by date desc '''
    orders = await database.fetch_all(query=query,
                                      values={
                                          'customer_id': customer_id,
                                      }
                                      )
    return [
        {
            'id': i.id,
            'title': i.title,
            'price': i.price,
            'date': i.date,
        } for i in orders
    ]


async def get_role_id(
        role: str
):
    try:
        query = '''SELECT id FROM public.roles where name ilike :role'''
        role_id = await database.fetch_one(query=query,
                                           values={
                                               'role': role
                                           }
                                           )
        return role_id.id
    except AttributeError:
        raise HTTPException(HTTPStatus.CONFLICT, detail='Illegal user role')


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
    query = '''select name,second_name,photo_url,phone_number,country from public.customers
        where customers.id= :id'''
    customer_info = await database.fetch_one(query, values={'id': id})
    if customer_info is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        'name': crypto_decode(customer_info.name),
        'second_name': crypto_decode(customer_info.second_name),
        'photo_url': customer_info.photo_url,
        'phone_number': customer_info.phone_number,
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
                                                               'price': price,
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


async def executor_approve(order_id, executor_id):
    query = '''UPDATE comments SET confirmed = True where order_id = :order_id and executor_id = :executor_id'''
    _ = await database.fetch_one(query,
                                 values={
                                     'order_id': order_id,
                                     'executor_id': executor_id
                                 }
                                 )
    query = '''SELECT id from comments where confirmed = True and order_id = :order_id and executor_id = :executor_id'''
    comment_data = await database.fetch_one(query,
                                            values={
                                                'order_id': order_id,
                                                'executor_id': executor_id
                                            }
                                            )
    query = '''select id from status where name =:name'''
    progress_status_id = await database.fetch_one(query,
                                                  values={
                                                      'name': 'progress'
                                                  })
    query = '''insert into deals values (:id,:comment_id, :deal_status_executor,:deal_status_customer,:files)'''
    create_deal = await database.fetch_one(query,
                                           values={
                                               'id': uuid.uuid4(),
                                               'comment_id': comment_data.id,
                                               'deal_status_executor': progress_status_id.id,
                                               'deal_status_customer': progress_status_id.id,
                                               'files': 'hui'
                                           }
                                           )


async def executor_reject(order_id, executor_id):
    query = '''UPDATE comments SET confirmed = False where order_id = :order_id and executor_id = :executor_id'''
    _ = await database.fetch_one(query,
                                 values={
                                     'order_id': order_id,
                                     'executor_id': executor_id
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
    query = '''SELECT id, title, price, date from public.orders where customer_id = :customer_id ORDER BY date desc'''
    orders_info = await database.fetch_all(query,
                                           values={
                                               'customer_id': customer_id,
                                           }
                                           )
    if orders_info is None:
        raise HTTPException(status_code=404, detail="This user doesn't have orders")
    return orders_info


async def get_list_executors():
    query = '''select avg(r.rating) as rating, exec.id, exec.name,exec.second_name,exec.photo_url,exec.
    phone_number,exec.country from public.executors exec
    left join public.reviews r on r.executor_id = exec.id
    GROUP BY exec.id,exec.name,exec.second_name,exec.photo_url,exec.phone_number,exec.country
    order by rating'''
    executors_info = await database.fetch_all(query)
    return [{
        'id': i.id,
        'name': crypto_decode(i.name),
        'second_name': crypto_decode(i.second_name),
        'photo_url': i.photo_url,
        'phone_number': i.phone_number,
        'country': i.country,
        'rating': i.rating
    } for i in executors_info]


async def info_about_order(order_id):
    query = '''SELECT * FROM orders ord
    left join deals d on d.comment_id = (select id from comments id where order_id = :order_id)
    join order_types ot on ord.type_id = ot.id
    where ord.id = :order_id'''
    orders_info = await database.fetch_one(query,
                                           values={
                                               'order_id': order_id,
                                           }
                                           )
    return {
        'title': orders_info.title,
        'description': orders_info.description,
        'files': orders_info.files,
        'price': orders_info.price,
        'date': orders_info.date,
        'type': orders_info.name
    }


async def update_order_customer_status(order_id, status_name, customer_id):
    query = '''update deals set deal_status_customer= (select id from status where name = :status) 
                                    where comment_id = (select id from comments where order_id = :order_id)'''
    status = await database.fetch_one(query,
                                      values={
                                          'order_id': order_id,
                                          'status': status_name
                                      }
                                      )
    query = '''SELECT name FROM public.status where id = (SELECT deal_status_executor FROM deals where 
    comment_id=(select id from public.comments where order_id = :order_id))'''
    executor_status = await database.fetch_one(query,
                                               values={
                                                   'order_id': order_id,
                                               }
                                               )
    if executor_status.name == 'done' and status_name == 'done':
        query = '''INSERT INTO public.basket values (:id, :order_id, :customer_id)'''
        _ = await database.fetch_one(query,
                                     values={
                                         'id': uuid.uuid4(),
                                         'order_id': order_id,
                                         'customer_id': customer_id
                                     }
                                     )


async def executor_done_orders(executor_id):
    query = '''SELECT id, title, price, date from public.orders 
    where id = (select order_id from comments where executor_id = :id and confirmed=True) and 
    id = ANY (SELECT completed_order_id from basket)'''
    done_orders_info = await database.fetch_all(query,
                                                values={
                                                    'id': executor_id,
                                                }
                                                )
    return [{
        'id': i.id,
        'title': i.title,
        'price': i.price,
        'date': i.date,
    } for i in done_orders_info]


async def executor_in_progress_orders(executor_id):
    query = '''SELECT id, title, price, date from public.orders 
    where id = (select order_id from comments where executor_id = :id and confirmed=True 
    and deal_status_executor = (select name from status where name='progress'))'''
    in_progress_orders_info = await database.fetch_all(query,
                                                       values={
                                                           'id': executor_id,
                                                       }
                                                       )
    return [
        {
            'id': i.id,
            'title': i.title,
            'price': i.price,
            'date': i.date,
        } for i in in_progress_orders_info
    ]


async def perform_executor_to_order(executor_id, order_id):
    query = '''INSERT INTO comments values (:id, :order_id, :executor_id, :confirmed)'''
    performing_executor = await database.fetch_one(query=query,
                                                   values={
                                                       'id': uuid.uuid4(),
                                                       'order_id': order_id,
                                                       'executor_id': executor_id,
                                                       'confirmed': False
                                                   })


async def update_order_executor_status(order_id, status_name, customer_id):
    query = '''update deals set deal_status_executor= (select id from status where name = :status) 
                                    where comment_id = (select id from comments where order_id = :order_id)'''
    status = await database.fetch_one(query,
                                      values={
                                          'order_id': order_id,
                                          'status': status_name
                                      }
                                      )
    query = '''SELECT name FROM public.status where id = (SELECT deal_status_customer FROM deals where 
    comment_id=(select id from public.comments where order_id = :order_id))'''
    executor_status = await database.fetch_one(query,
                                               values={
                                                   'order_id': order_id,
                                               }
                                               )
    if executor_status.name == 'done' and status_name == 'done':
        query = '''INSERT INTO public.basket values (:id, :order_id, :customer_id)'''
        _ = await database.fetch_one(query,
                                     values={
                                         'id': uuid.uuid4(),
                                         'order_id': order_id,
                                         'customer_id': customer_id
                                     }
                                     )


async def get_types():
    query = '''SELECT name from public.order_types'''
    order_types = await database.fetch_all(query)
    return order_types


async def get_customer_info_by_id(customer_id):
    query = '''Select id, email,name,second_name,photo_url,phone_number,country,city from customers where id=:id'''
    executor_data = await database.fetch_one(query,
                                             values={
                                                 'id': customer_id,
                                             }
                                             )
    return {
        'id': executor_data.id,
        'email': crypto_decode(executor_data.email),
        "name": crypto_decode(executor_data.name),
        "second_name": crypto_decode(executor_data.second_name),
        "photo_url": executor_data.photo_url,
        "phone_number": executor_data.phone_number,
        "country": executor_data.country,
        "city": executor_data.city
    }


async def get_executor_info_by_id(executor_id):
    query = '''Select id, email,name,second_name,photo_url,phone_number,country,city from executors where id=:exec_id'''
    executor_data = await database.fetch_one(query,
                                             values={
                                                 'exec_id': executor_id,
                                             }
                                             )
    return {
        'id': executor_data.id,
        'email': crypto_decode(executor_data.email),
        "name": crypto_decode(executor_data.name),
        "second_name": crypto_decode(executor_data.second_name),
        "photo_url": executor_data.photo_url,
        "phone_number": executor_data.phone_number,
        "country": executor_data.country,
        "city": executor_data.city
    }
