from sqlalchemy import Column, String, DateTime, func
from app.repository.db_setup import Base
import uuid

class AuthToken(Base):
    __tablename__ = "auth_tokens"

    token_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    username = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    platform = Column(String, nullable=False)  # Platform identifier (e.g., "web", "mobile", etc.)
    current_time = Column(DateTime, default=func.now(), nullable=False)
    last_login_time = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<AuthToken(token_id={self.token_id}, username={self.username}, platform={self.platform}, access_token={self.access_token}, refresh_token={self.refresh_token}, current_time={self.current_time}, last_login_time={self.last_login_time})>"