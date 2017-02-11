import datetime as dt
import time
import os
import threading
import tempfile
import sqlalchemy as sql
import pytest

from unichat import RelationBase, Message, Person, Thread

@pytest.fixture
def make_session():
  (_, db_path) = tempfile.mkstemp(dir='/tmp', prefix='unichat__test_relations', suffix='.db')
  engine = sql.create_engine('sqlite:///'+db_path) # this needs to be an ACTUAL FILE, per http://docs.sqlalchemy.org/en/rel_0_9/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
  RelationBase.metadata.create_all(engine)
  yield sql.orm.scoped_session(sql.orm.sessionmaker(bind=engine))
  os.remove(db_path)

def test_basic_object_persistence(make_session):
  now = dt.datetime.now()
  session = make_session()
  t = Thread(name='Test thread!')
  p = Person(name='Spencer')
  m = Message(time=now, thread=t, speaker=p, content='hi')
  session.add_all([t, p, m])
  session.commit()
  session.close()

  session = make_session()
  assert session.query(Thread).one().name == 'Test thread!'
  assert session.query(Person).one().name == 'Spencer'
  m = session.query(Message).one()
  assert m.time == now
  assert m.content == 'hi'
  assert m.thread_name == m.thread.name == 'Test thread!'
  assert m.speaker_name == m.speaker.name == 'Spencer'


def test_scoped_session_can_modify_db_from_multiple_threads(make_session):
  def create_a_person(name):
    session = make_session()
    session.add(Person(name=name))
    time.sleep(0.05)
    session.commit()
    make_session.remove()

  t1 = threading.Thread(target=lambda: create_a_person('one'))
  t2 = threading.Thread(target=lambda: create_a_person('two'))
  t1.start(); t2.start(); t1.join(); t2.join()

  session = make_session()
  assert {p.name for p in session.query(Person)} == {'one', 'two'}
