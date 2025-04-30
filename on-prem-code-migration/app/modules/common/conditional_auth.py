from functools import wraps
from IAM.authorization.shop_authorizer import shop_auth
from IAM.authorization.psm_download_authorizer import psm_download
from IAM.authorization.base import authorize


def conditional_authorize(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        role = kwargs.get('role')
        if role:
            return authorize(shop_auth)(func)(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper


def conditional_download_authorize(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        role = kwargs.get('role')
        if role:
            return authorize(psm_download)(func)(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper
