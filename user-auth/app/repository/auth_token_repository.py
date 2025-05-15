from sqlalchemy.orm import Session
from app.models.auth_token import AuthToken
from datetime import datetime, timezone

class AuthTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_auth_token(self, username: str, access_token: str, refresh_token: str, platform: str, last_login_time=None):
        """
        Create a new auth token for a user on a specific platform.
        """
        auth_token = AuthToken(
            username=username,
            access_token=access_token,
            refresh_token=refresh_token,
            platform=platform,
            last_login_time=last_login_time,
        )
        self.db.add(auth_token)
        self.db.commit()
        return auth_token

    def get_auth_tokens_by_username(self, username: str):
        """
        Retrieve all auth tokens for a user.
        """
        return self.db.query(AuthToken).filter(AuthToken.username == username).all()
    
    def update_access_token(self, username: str, refresh_token: str, new_access_token: str):
        """
        Update the access token for a specific user in the database.
        """
        try:
            # Find the user's auth token record
            auth_token = self.db.query(AuthToken).filter(AuthToken.username == username, AuthToken.refresh_token == refresh_token).first()
            if auth_token:
                # Update the access token and the updated_at timestamp
                auth_token.access_token = new_access_token
                auth_token.current_time = datetime.now(timezone.utc)  # Optional: Update the timestamp
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_auth_token_by_access_token(self, username: str, access_token: str):
        """
        Delete an auth token by its access token.
        """
        auth_token = self.db.query(AuthToken).filter(AuthToken.username == username, AuthToken.access_token == access_token).first()
        if auth_token:
            self.db.delete(auth_token)
            self.db.commit()
            return True
        return False