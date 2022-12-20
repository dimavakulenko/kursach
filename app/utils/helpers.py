from logging import getLogger
import json
import zlib
import base64
from typing import Optional
from datetime import datetime, timedelta, time
from cryptography.fernet import Fernet
import jwt

from app.config import config

log = getLogger(config.APP_NAME)

token_expiration_time = config.JWT_TOKEN_EXPIRATION_TIME
key_token = config.SECRET_TOKEN_KEY


def create_access_token(data: dict):
    to_encode = data.copy()
    access_token_expires = datetime.utcnow() + timedelta(minutes=token_expiration_time)
    to_encode.update({"exp": access_token_expires})
    encoded_jwt = jwt.encode(to_encode, key_token, algorithm='HS256')
    return encoded_jwt


def decode_access_token(jwt_token):
    data = jwt.decode(jwt_token, key_token, algorithms=["HS256"])
    return data


def crypto_encode(params):
    encrypted_text = base64.b64encode(params.encode('utf-8'))
    return encrypted_text


def crypto_decode(params):
    asd =params.encode('utf-8')
    decrypted_text = base64.b64decode(params.encode('utf-8') + b'==')
    return decrypted_text


def user_information_encoder(params):
    f = Fernet(key_token)

    data = json.dumps(params, sort_keys=True)
    data = zlib.compress(data.encode('utf-8'))
    token = f.encrypt(data)

    return token


def user_information_decoder(click_id):
    f = Fernet(key_token)

    token = f.decrypt(click_id)
    token = zlib.decompress(token)
    token = json.loads(token)

    return token