from datetime import datetime
from logging import getLogger
import json
import zlib
import base64
from cryptography.fernet import Fernet

from app.config import config

log = getLogger(config.APP_NAME)


key_token = config.SECRET_TOKEN_KEY


def crypto_encode(params):
    encrypted_text = base64.b64encode(params.encode('utf-8'))
    return encrypted_text


def crypto_decode(params):
    decrypted_text = base64.b64decode(params).decode('utf-8')
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