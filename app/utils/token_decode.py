from fastapi import HTTPException
from fastapi.params import Header

from app.utils.helpers import decode_access_token


class Token:
    def __init__(
            self,
            authorisation: str = Header(description='Токен авторизации'),
    ):
        try:
            self.token_data = decode_access_token(authorisation)
        except Exception:
            raise HTTPException(status_code=401, detail='illegal user token')