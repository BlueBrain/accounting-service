from sqlalchemy import MetaData

from app.db import model as test_module


def test_metadata():
    assert isinstance(test_module.Base.metadata, MetaData)
