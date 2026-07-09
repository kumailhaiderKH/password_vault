from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_username: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    client_id: str
    client_secret: str
    redirect_uri: str
    sendgrid_api_key: str    
    sender_email: str 
    encryption_key_1: str
    encryption_key_2: str
    encryption_key_3: str
    current_key_version: int
    rate_limit_requests: int = 5
    rate_limit_window: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()