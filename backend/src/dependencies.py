from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from .utils import verify_token
from .schemas.user import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = verify_token(token)
    username = payload.get("sub")

    return TokenData(username=username)