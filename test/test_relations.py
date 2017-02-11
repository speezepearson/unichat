import datetime as dt
import time
import threading

from unichat import Message, Person, Thread

from . import make_session

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
