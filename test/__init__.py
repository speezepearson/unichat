import os
import tempfile

import sqlalchemy
import pytest

import unichat

@pytest.fixture
def make_session():
  (_, db_path) = tempfile.mkstemp(dir='/tmp', prefix='unichat__test_relations', suffix='.db')
  engine = sqlalchemy.create_engine('sqlite:///'+db_path) # this needs to be an ACTUAL FILE, per http://docs.sqlalchemy.org/en/rel_0_9/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
  unichat.RelationBase.metadata.create_all(engine)
  yield sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=engine))
  os.remove(db_path)
