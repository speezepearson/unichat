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

def iter_messages(get_username_from_id, get_channelname_from_id):
  p = subprocess.Popen(['node', os.path.join(HERE, 'fetch.js')], stdout=subprocess.PIPE)
  for fb_threadid, fb_speakerid, content in csv.reader(io.TextIOWrapper(p.stdout)):
    logger.debug('got message: {}'.format((fb_threadid, fb_speakerid, content)))
    yield Message(
      time=dt.datetime.now(),
      thread=get_channelname_from_id(fb_threadid),
      speaker=get_username_from_id(fb_speakerid),
      content=content)

def send_messages(messages, get_channelid_from_name):
  p = subprocess.Popen(['node', os.path.join(HERE, 'send.js')], stdin=subprocess.PIPE)
  sio = io.StringIO()
  writer = csv.DictWriter(sio, fieldnames=Message._fields)
  writer.writeheader()
  for message in messages:
    print('writing:', message)
    writer.writerow(message._replace(thread=get_channelid_from_name(message.thread))._asdict())
    p.stdin.write(sio.getvalue().encode() + b'\n')
    p.stdin.flush()
    sio.seek(0)
    sio.truncate()
  p.stdin.close()
  p.wait()
