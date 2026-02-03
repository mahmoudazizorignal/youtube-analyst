from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BRIGHT_DATA_API_KEY: str
    BRIGHT_DATA_API_COUNTRY_CODE: str
    BRIGHT_DATA_API_ENDPOINT: str
    BRIGHT_DATA_API_ORDER_BY: str
    BRIGHT_DATA_API_POSTS_COUNT: int
    BRIGHT_DATA_API_OUTPUT_FORMAT: str
    
    OLLAMA_MODEL_ID: str
    OLLAMA_URL: str
    
    VIDEOS_PER_ROW: int

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
