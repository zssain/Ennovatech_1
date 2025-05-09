from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DB_HOST: str
    DB_PORT: int
    DB_SERVICE: str
    DB_USER: str
    DB_PASSWORD: str
    
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application settings
    APP_NAME: str = "HR Management System"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings() 