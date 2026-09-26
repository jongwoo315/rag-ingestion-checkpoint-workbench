from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./workbench.db"
    mock_embedding_dim: int = 128
    chunk_size: int = 256


settings = Settings()
