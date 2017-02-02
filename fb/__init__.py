import datetime as dt
import csv
import subprocess
import os
import logging
import io
from .. import Message, write_messages_to_csv

HERE = os.path.dirname(__file__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Client:
  def __init__(self):
    self.process = subprocess.Popen(['node', os.path.join(HERE, 'client.js')], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # self.process = subprocess.Popen(['cut','-d',',','-f','2-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    self._sending_buffer = io.StringIO()
    self._sending_writer = csv.DictWriter(self._sending_buffer, fieldnames=Message._fields)
    self._sending_writer.writeheader()
    self._receiving_reader = csv.reader(io.TextIOWrapper(self.process.stdout))

  def send(self, message):
    logger.info('sending {} to Facebook'.format(message))
    self._sending_writer.writerow(message._replace(thread=message.thread)._asdict())
    self.process.stdin.write(self._sending_buffer.getvalue().encode() + b'\n')
    logger.debug('wrote {!r} to client subprocess'.format(self._sending_buffer.getvalue().encode() + b'\n'))
    self.process.stdin.flush()
    self._sending_buffer.seek(0)
    self._sending_buffer.truncate()

  def read(self):
    r = next(self._receiving_reader)
    logger.info('received {} from Facebook'.format(r))
    fb_threadid, fb_speakerid, content = r
    return Message(
      time=dt.datetime.now(),
      thread=fb_threadid,
      speaker=fb_speakerid,
      content=content)

def iter_messages(client, get_username_from_id, get_channelname_from_id):
  while True:
    m = client.read()
    yield m._replace(
      thread=get_channelname_from_id(m.thread),
      speaker=get_username_from_id(m.speaker),
    )

def send_messages(messages, client, get_channelid_from_name):
  for m in messages:
    client.send(m._replace(thread=get_channelid_from_name(m.thread)))
