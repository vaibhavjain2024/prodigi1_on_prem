from fastapi import HTTPException, Request
from app.config.config import VERIFY_AUTH_URL
from functools import wraps
import requests
import traceback


def get_user_data(token_str):
    headers = {
        "Authorization": token_str
    }
    response = requests.get(VERIFY_AUTH_URL, headers=headers)
    return response


def jwt_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        print(args, kwargs)
        request: Request = kwargs.get('request')
        token_str = request.headers.get("Authorization", False)

        if not token_str:
            raise HTTPException(status_code=401, detail="Token is missing in Headers")

        try:
            response = get_user_data(token_str)
            result = response.json()

            if result and result.get("status_code", 401) != 200:
                raise HTTPException(status_code=401, detail=f"Unauthorized {response.text}")
            
            user_data = result.get("data", {})
            username = user_data.get("sub")

            request.state.user_data = user_data
            request.state.username = username
            request.state.tenant = user_data.get("tenant", "")
            request.state.email = user_data.get("email_id", "")
            print(request.state.user_data, request.state.username, request.state.email)
            return await func(*args, **kwargs)
        except Exception as exc:
            traceback.print_exc()
            raise HTTPException(status_code=401, detail=str(exc))
    return wrapper
