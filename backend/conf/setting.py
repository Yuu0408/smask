from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from sqlmodel import create_engine
from sqlalchemy import Engine
from functools import cached_property
from urllib.parse import quote_plus

class Settings(BaseSettings):
    PG_HOST: str = Field(alias="PG_HOST", default="postgres")
    PG_PORT: int = Field(alias="PG_PORT", default=5432)
    PG_USER: str = Field(alias="PG_USER", default="postgres")
    PG_PASSWORD: str = Field(alias="PG_PASSWORD", default="123456")
    PG_DB: str = Field(alias="PG_DB", default="postgres")
    
    # For debugging only
    PG_ECHO: bool = Field(alias="PG_ECHO", default=False)

    @computed_field
    @cached_property
    def SQL_ENGINE(self) -> Engine:
        DATABASE_URL = f"postgresql+psycopg2://{self.PG_USER}:{quote_plus(self.PG_PASSWORD)}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"
        return create_engine(DATABASE_URL, echo=self.PG_ECHO)
    
    def SQL_URL(self) -> str:
        return f"postgresql+psycopg2://{self.PG_USER}:{quote_plus(self.PG_PASSWORD)}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

settings = Settings()