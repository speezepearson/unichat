import datetime as dt
import csv
import subprocess
import os
import logging
import io
from sqlalchemy_bonus import get_or_create
from ... import Message, Thread, Person

HERE = os.path.dirname(__file__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Client:
  def __init__(self, email, password, db_session):
    self.email = email
    self.password = password
    self.db_session = db_session
    self.process = None
    self._sending_buffer = None
    self._sending_writer = None
    self._receiving_reader = None

  def __enter__(self):
    self.process = subprocess.Popen(['node', os.path.join(HERE, 'client.js')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env={'FB_EMAIL': self.email, 'FB_PASSWORD': self.password})
    self._sending_buffer = io.StringIO()
    self._sending_writer = csv.DictWriter(self._sending_buffer, fieldnames=['time', 'thread', 'speaker', 'content'])
    self._sending_writer.writeheader()
    self._receiving_reader = csv.reader(io.TextIOWrapper(self.process.stdout))
    return self

  def __exit__(self, *args):
    self.process.kill()
    self.process.wait()

  def send_message(self, message):
    logger.info('sending {} to Facebook'.format(message))
    self._sending_writer.writerow({
      'time': message.time.strftime('%Y-%m-%D %H:%M:%S.%f'),
      'thread': message.thread.fb_id,
      'speaker': message.speaker.fb_id,
      'content': message.content})
    self.process.stdin.write(self._sending_buffer.getvalue().encode() + b'\n')
    logger.debug('wrote {!r} to client subprocess'.format(self._sending_buffer.getvalue().encode() + b'\n'))
    self.process.stdin.flush()
    self._sending_buffer.seek(0)
    self._sending_buffer.truncate()

  def send_messages(self, messages):
    for message in messages:
      self.send_message(message)

  def read_message(self):
    r = next(self._receiving_reader)
    logger.info('received {} from Facebook'.format(r))
    fb_threadid, fb_speakerid, content = r
    thread = get_or_create(self.db_session, Thread, fb_id=fb_threadid, defaults={'name': 'Facebook thread '+fb_threadid})
    speaker = get_or_create(self.db_session, Person, fb_id=fb_speakerid, defaults={'name': fb_speakerid+'@facebook.com'})

    return Message(
      time=dt.datetime.now(),
      thread=thread,
      speaker=speaker,
      content=content)

  def read_messages(self):
    while True:
      yield self.read_message()
