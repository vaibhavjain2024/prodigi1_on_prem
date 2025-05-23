from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str
    ldap_bind: Optional[bool] = Field(default=True)  # Indicates if LDAP binding is required
    platform: Optional[str] = Field(default="web")  # Platform identifier (e.g., "web", "mobile", etc.)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ResetPasswordRequest(BaseModel):
    username: str
    new_password: str
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"