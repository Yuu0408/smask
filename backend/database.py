from sqlmodel import Session, SQLModel
from conf.setting import settings
from models.entities.model import *
from models.entities.contact_models import *
import logging

engine = settings.SQL_ENGINE

logger = logging.getLogger(__name__)

def create_db_and_tables():
    logger.info("Attempting to create tables")
    SQLModel.metadata.create_all(engine)
    logger.info("Finishing creating tables")

def get_session():
    with Session(engine) as session:
        yield session
