import sys
from pathlib import Path

# افزودن ریشه پروژه به مسیر ایمپورت‌ها
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from inventory_core.database import Base
from inventory_core import models
import sys
import os

# اضافه کردن ریشه پروژه (پوشه والد tests) به sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def engine():
    _engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=_engine)
    return _engine


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
