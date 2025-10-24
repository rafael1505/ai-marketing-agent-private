import secrets
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import validator, ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="allow")
    
    PROJECT_NAME: str = "AI Marketing Agent"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "default_secret_key_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "ai_marketing_agent"
    
    # CORS - simplified handling for Docker environment
    CORS_ORIGINS: List[str] = ["http://localhost:3001", "http://frontend:3001"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # AI Provider Settings
    DEFAULT_AI_PROVIDER: str = "openai"  # Can be changed based on requirements

settings = Settings()
