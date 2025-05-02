from fastapi import APIRouter, Header, Request, HTTPException
from datetime import datetime, timedelta, timezone
from modules.IAM.repositories.user_repository import UserRepository
from modules.IAM.services.user_service import UserService
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_jwt_token
from app.auth.ldap_auth import authenticate_ldap, reset_password_ldap
from app.repository.auth_token_repository import AuthTokenRepository
from app.schema.userSchema import ResetPasswordRequest, LoginRequest, RefreshTokenRequest
from app.session_helper import SessionHelper
from app.utils.validate_password_utility import validate_password
from app.utils.cloudwatch_logs import log_to_cloudwatch
from app.utils.logger_utility import logger
from app.utils.rate_limiter import limiter
from app.utils import constants
from app.config import config
import traceback
import json

router = APIRouter()

@router.post("/login")
# @limiter.limit("5/minute")  # Allow 5 login attempts per minute per IP
async def login(request: Request, body: LoginRequest):
    """
        Endpoint to log in a user.

        This endpoint authenticates a user using LDAP, checks if the user exists in the prodigi1 user data table,
        and generates access and refresh tokens if the authentication is successful.

        Args:
            request (Request): The HTTP request object containing the username, password, and device ID in the body.

        Returns:
            dict: A dictionary containing the access token, refresh token, token type, and status code if the login is successful.
                  Otherwise, it returns an error message and status code.
    """
    try:
        log_to_cloudwatch("INFO", f"Event received at login API POST /login : {body.username}")
        user_name = body.username
        user_password = body.password
        platform = body.platform
        utc_login_time = datetime.now(timezone.utc)
        user_name_without_maruti_lower =  user_name.split("\\")[-1].lower()

        rbac_session = SessionHelper(config.PLATFORM_CONNECTION_STRING).get_session()  
        user_repository = UserRepository(rbac_session)
        user_service = UserService(user_repository)        

        is_ldap_authenticated = await authenticate_ldap(user_name, user_password)
        log_message = f"Response for authenticate_ldap {is_ldap_authenticated} and Username {user_name}"
        logger.info(log_message)
        log_to_cloudwatch("INFO", log_message)

        # check user in Prodigi1 user data table
        is_user_exist_in_user_data = user_service.get_user_by_federation_identifier(user_name_without_maruti_lower)
        log_message = f"Response: for get_user_by_username user {user_name_without_maruti_lower} "
        logger.info(log_message)
        log_to_cloudwatch("INFO", log_message)
        if is_user_exist_in_user_data and is_ldap_authenticated:
            claim_data = {
                "federation_identifier": is_user_exist_in_user_data["federation_identifier"],
                "role_permissions": is_user_exist_in_user_data["role_permissions"],
                "is_admin": is_user_exist_in_user_data["is_admin"],
                "is_super_admin": is_user_exist_in_user_data["is_super_admin"],
                "tenant": is_user_exist_in_user_data["tenant"],
                "last_login": str(utc_login_time)
            }

            access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": user_name_without_maruti_lower}, expires_delta=access_token_expires, claims=claim_data)
            refresh_token_expires = timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = create_refresh_token(data={"sub": user_name_without_maruti_lower}, expires_delta=refresh_token_expires,claims= claim_data)
            
            # Store tokens in the database
            auth_token_repo = AuthTokenRepository(rbac_session)
            auth_token_repo.create_auth_token(
                username=user_name_without_maruti_lower,
                access_token=access_token,
                refresh_token=refresh_token,
                platform=platform,
                last_login_time=utc_login_time,
            )

            log_message = f"Tokens generated for user {user_name_without_maruti_lower}"
            logger.info(log_message)
            log_to_cloudwatch("INFO", log_message)

            return {
                "data":{
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                },
                "status_code":"200",
                "msg": "Token details."
            }
        
        return dict (
            status_code=401,
            data = {},
            msg = "Invalid creadentials"
        )
    except Exception as exc:
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)
        log_to_cloudwatch("ERROR", exception_traceback)
        return dict (
            status_code=401,
            data = {},
            msg = str(exc)
        )


@router.post("/refresh/token")
# @limiter.limit("5/minute")  # Allow 5 login attempts per minute per IP
async def refresh_token(request: Request, body: RefreshTokenRequest):
    """
        Endpoint to refresh the JWT access token.

        This endpoint takes a refresh token from the request body, decodes it, and generates a new access token if the refresh token is valid.
        It also updates the access token in the database.

        Args:
            request (Request): The HTTP request object containing the refresh token in the body.

        Returns:
            dict: A dictionary containing the new access token, refresh token, token type, and status code.
    """
    log_to_cloudwatch("INFO", f"Event received at refresh/token: body: {body}")
    try:
        refresh_token = body.refresh_token
        payload = decode_jwt_token(refresh_token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid/expired refresh token, login again")
        
        username = payload.get("sub")
        utc_login_time = payload.get("last_login","")

        rbac_session = SessionHelper(config.PLATFORM_CONNECTION_STRING).get_session()  
        user_repository = UserRepository(rbac_session)
        user_service = UserService(user_repository)    

        # check user in Prodigi1 user data table
        user = user_service.get_user_by_federation_identifier(username)
        log_message = f"Response: for get_user_by_username user {username} "
        logger.info(log_message)
        log_to_cloudwatch("INFO", log_message)

        if not user:
            log_message = f"User {username} not found in the user data collection"
            logger.error(log_message)
            log_to_cloudwatch("ERROR", log_message)
            raise HTTPException(status_code=401, detail="User not exist")
        
        claim_data = {
                "federation_identifier": user["federation_identifier"],
                "role_permissions": user["role_permissions"],
                "is_admin": user["is_admin"],
                "is_super_admin": user["is_super_admin"],
                "tenant": user["tenant"],
                "last_login": utc_login_time
            }
        
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user['federation_identifier']}, expires_delta=access_token_expires, claims=claim_data)
        
        # Update access tokens in the database
        auth_token_repo = AuthTokenRepository(rbac_session)
        is_updated = auth_token_repo.update_access_token(
                            username=user["federation_identifier"],
                            refresh_token=refresh_token,
                            new_access_token=access_token
                        )

        if not is_updated:
            raise HTTPException(status_code=404, detail="User not found or refresh token update failed")

        return dict(
            status_code=200,
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
            msg="User token generated."
        )
    except Exception as exc:
        log_message = f"Exception occurred during token refresh: {str(exc)}"
        logger.error(log_message)
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)
        log_to_cloudwatch("ERROR", exception_traceback)

        return dict (
            status_code=401,
            data = {},
            msg = str(exc)
        )


@router.get("/verify/token")
async def verify_token(Authorization: str = Header(...)):
    """
        Endpoint to verify the JWT token.

        This endpoint checks the validity of the provided JWT token, verifies the user, and returns the user details if the token is valid.

        Args:
            request (Request): The HTTP request object containing the Authorization header with the JWT token.

        Returns:
            dict: A dictionary containing the response message, response code, and user details if the token is valid.
    """
    try:
        # Extract the token from the "Bearer <token>" format
        if not Authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
        token = Authorization.split(" ")[1]
        payload = decode_jwt_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid/expire token")

        return dict(
            status_code=200,
            data=payload,
            msg="User authorized"
        )

    except Exception as exc:
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)
        log_to_cloudwatch("ERROR", exception_traceback)
        return dict(
            status_code=503,
            data={},
            msg=str(exc)
        )


@router.post("/logout")
async def logout(Authorization: str = Header(...)):
    """
        Endpoint to log out a user.

        This endpoint logs out a user by deleting their authentication token from the database.

        Args:
            request (Request): The HTTP request object containing the Authorization header with the JWT token.

        Returns:
            dict: A dictionary containing the response message and response code.
    """
    try:
        if not Authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        
        token = Authorization.split(" ")[1]
        payload = decode_jwt_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid/expire token")

        # Extract username from token payload
        username = payload.get("sub")

        rbac_session = SessionHelper(config.PLATFORM_CONNECTION_STRING).get_session()  
        auth_token_repo = AuthTokenRepository(rbac_session)
        is_logout = auth_token_repo.delete_auth_token_by_access_token(
                            username=username,
                            access_token=token
                        )
        
        if not is_logout:
            raise HTTPException(status_code=404, detail="User not found or token deletion failed")

        return dict(
            status_code=200,
            data={},
            msg="User logged out successfully"
        )
    except Exception as exc:
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)
        log_to_cloudwatch("ERROR", exception_traceback)
        return dict(
					status_code=503,
					data={},
					msg=str(exc)
				)


@router.post("/reset-password")
async def reset_password(request: Request, reset_request: ResetPasswordRequest):
    """
        @function(name: "msil-iot-reset-password")

        Endpoint to reset the password using LDAP.

        This endpoint validates the provided token, checks if the logged-in user matches the username in the request,
        validates the new password, and then calls the LDAP service to reset the password.

        Args:
            request (Request): The HTTP request object.
            reset_request (ResetPasswordRequest): The request body containing the username and new password.

        Returns:
            dict: A dictionary containing the response message and response code.
    """
    logger.info(f"Received request for Reset-Password: {reset_request}")
    try:
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Token is missing in Headers")

        token = token.split(" ")[1]
        payload = decode_jwt_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid/expire token")

        username = payload.get("sub")
        if username != reset_request.username:
            message = f"Username {username} does not match."
            logger.warning(message)
            log_to_cloudwatch("WARNING", message)
            return {
                "response": {},
                "message": "User not found",
                "responseCode": constants.STATUS_CODES.get(constants.RESOURCE_NOT_FOUND), # PC404
            }
        
        if not validate_password(reset_request.new_password):
            message = "Password validation failed"
            logger.warning(message)
            log_to_cloudwatch("WARNING", message)
            return {
                "response": {},
                "message": message,
                "responseCode": "PC400",
            }

        # Call LDAP service to reset password
        ldap_result = await reset_password_ldap(reset_request.username, reset_request.new_password)

        if ldap_result is None:
            message = "Failed to reset password in LDAP"
            logger.warning(message)
            log_to_cloudwatch("WARNING", message)
            return {
                "response": {},
                "message": message,
                "responseCode": "PC500",
            }

        # Success case: password reset
        message = "Password reset successfully"
        logger.info(message)
        log_to_cloudwatch("INFO", message)
        return {
            "response": {},
            "message": message,
            "responseCode": constants.STATUS_CODES.get(constants.SUCCESS)  # Assuming constants map to status codes
        }

    except Exception as exc:
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)
        log_to_cloudwatch("ERROR", exception_traceback)
        return dict(
					status_code=503,
					data={},
					msg=str(exc)
				)