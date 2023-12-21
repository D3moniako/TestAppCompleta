from typing import Generator
from sqlmodel import create_engine, Session
from sqlalchemy import engine
from pyramid.config import Configurator

#################
import os
DB_CONFIG = {
    "db_name": os.getenv("DB_NAME", "dockerdb"),
    "db_user": os.getenv("DB_USER", "postgres"),
    "db_password": os.getenv("DB_PASSWORD", "toor"), ## PASSWORD DA RICORDARE!!!
    "db_port": os.getenv("DB_PORT", "5432"),
    "db_host": os.getenv("DB_HOST", "localhost"), #nome oppure ip
}

def get_db():
    try:
        config = Configurator()
        config.scan(
            # "app.src.models"    # senza docker user_management_service.models
            "."  ###IMPORTANTE NON CANCELLARE è IL PATH DA CUI  CARICA I MODELLI
            
        )  # need to scan a folder and import classes and models
        engine = get_engine()
    except IOError:
        # logger.exception("Failed to get database connection!")
        return None, "fail"

    return engine
#MI DA LA SESSIONE
def get_session_local():
    engine = get_db()
    return Session(bind=engine)

# define postgres sqlalchemy engine connection
def get_engine() -> engine:
    """
    Sets up database connection from config database dict.
    """
    if not (
        "db_host" in DB_CONFIG.keys()
        and "db_user" in DB_CONFIG.keys()
        and "db_password" in DB_CONFIG.keys()
        and "db_name" in DB_CONFIG.keys()
        and "db_port" in DB_CONFIG.keys()
    ):
        raise Exception("Bad config file: " + DB_CONFIG)

    url = "postgresql://{user}:{passwd}@postgres:{port}/{db}".format(
    user=DB_CONFIG["db_user"],
    passwd=DB_CONFIG["db_password"],
    port=DB_CONFIG["db_port"],
    db=DB_CONFIG["db_name"],
)

    engine = create_engine(url=url, pool_size=50)
    return engine


# get engine sqlalchemy session

def get_session() -> Generator:
    engine = get_db()
    with Session(engine) as session:
        yield session

# get engine sqlmodel session
def get_session_sqlmodel():
    engine = get_db()
    session = Session(engine)
    return session

