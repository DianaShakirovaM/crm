from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Mini CRM'
    VERSION: str = '1.0.0'
    API_V1_STR: str = '/api/v1'
    # Database
    DATABASE_URL: str = 'sqlite:///./crm.db'
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ['http://localhost:3000']

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
