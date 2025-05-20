from sqlalchemy.orm import Session
from app.models.auth_token import AuthToken
from datetime import datetime, timezone

class AuthTokenRepository:
    def __init__(self, db: Session):
        self.session = db

    def create_auth_token(self, username: str, access_token: str, refresh_token: str, platform: str, last_login_time=None):
        """
        Create a new auth token for a user on a specific platform.
        """
        with self.session as session:
            auth_token = AuthToken(
                username=username,
                access_token=access_token,
                refresh_token=refresh_token,
                platform=platform,
                last_login_time=last_login_time,
            )
            session.add(auth_token)
            return auth_token

    def get_auth_tokens_by_username(self, username: str):
        """
        Retrieve all auth tokens for a user.
        """
        with self.session as session:
            return session.query(AuthToken).filter(AuthToken.username == username).all()
    
    def update_access_token(self, username: str, refresh_token: str, new_access_token: str):
        """
        Update the access token for a specific user in the database.
        """
        with self.session as session:
            # Find the user's auth token record
            auth_token = session.query(AuthToken).filter(AuthToken.username == username, AuthToken.refresh_token == refresh_token).first()
            if auth_token:
                # Update the access token and the updated_at timestamp
                auth_token.access_token = new_access_token
                auth_token.current_time = datetime.now(timezone.utc)  # Optional: Update the timestamp
                return True
            return False
    
    def delete_auth_token_by_access_token(self, username: str, access_token: str):
        """
        Delete an auth token by its access token.
        """
        with self.session as session:
            auth_token = session.query(AuthToken).filter(AuthToken.username == username, AuthToken.access_token == access_token).first()
            if auth_token:
                session.delete(auth_token)
                return True
            return False