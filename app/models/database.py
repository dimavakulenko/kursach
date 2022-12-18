from enum import Enum
import uuid
from sqlalchemy import Column, Integer, Text, Date, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import INET, MONEY, DATE, UUID

Base = declarative_base()


class Executor(Base):
    __tablename__ = "executors"

    id = Column(UUID, primary_key=True, index=True)
    email = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    second_name = Column(Text, nullable=False)
    birth_date = Column(Date, nullable=False)
    photo_url = Column(INET)
    phone_number = Column(Text, nullable=False)
    country = Column(Text)
    city = Column(Text)
    role = Column(Text, nullable=False)


executor = Executor.__table__


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID, primary_key=True, index=True)
    email = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    second_name = Column(Text, nullable=False)
    birth_date = Column(Date, nullable=False)
    photo_url = Column(INET)
    phone_number = Column(Text, nullable=False)
    country = Column(Text)
    city = Column(Text)
    role = Column(Text, nullable=False)


class OrderTypes(Base):
    __tablename__ = "order_types"

    id = Column(UUID, primary_key=True)
    names = Column(Text)
    description = Column(Text)


order_types = OrderTypes.__table__


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey('executors.id'))
    title = Column(Text)
    description = Column(Text)
    files = Column(INET)
    status = Column(Text)
    price = Column(MONEY)
    type = Column(UUID, ForeignKey('order_types.id'))
    executor_id = Column(UUID, ForeignKey('executors.id'))


order = Order.__table__


class Wallets(Base):
    __tablename__ = "wallets"

    id = Column(UUID, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey('executors.id'), index=True)
    amount = Column(MONEY, default=0, nullable=False)

#
# class Roles(Base):
#     __tablename__ = "roles"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
