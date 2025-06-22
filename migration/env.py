from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import os
from alembic import context
import sqlmodel
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

from src.models import AnnotatorStat

load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option('sqlalchemy.url', os.environ["DATABASE_URL"])


db_url = os.environ["DATABASE_URL"]

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = sqlmodel.SQLModel.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url", db_url)
    url = db_url
    if not url:
        raise RuntimeError("DATABASE_URL environment variable not set")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=pool.NullPool,
    )

    
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn, 
                target_metadata=target_metadata
            )
        )
        
        # Fix the argument error here
        await connection.run_sync(lambda _: context.run_migrations())


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()


import asyncio

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())