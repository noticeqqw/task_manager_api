from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Импортируем Base из нашего проекта
from app.db.session import Base

# Импортируем все модели чтобы они зарегистрировались в Base.metadata
from app.models.user import User  # noqa: F401

# Загружаем переменную окружения DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

config = context.config

# Устанавливаем URL базы в конфиг Alembic
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Настройка логирования Alembic
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск миграций в offline режиме (без подключения к БД)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Запуск миграций в online режиме"""
    # Используем DATABASE_URL напрямую
    url = config.get_main_option("sqlalchemy.url")
    
    if not url:
        raise ValueError("sqlalchemy.url не установлена в конфиге или переменной окружения DATABASE_URL")
    
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
