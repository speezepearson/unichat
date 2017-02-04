import time
import datetime as dt
import logging
import slackclient
from sqlalchemy_bonus import get_or_create
from . import Message, Thread, Person

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)

class Client:
  def __init__(self, slack_client, db_session):
    self.slack_client = slack_client
    self.db_session = db_session

  def __enter__(self):
    if not self.slack_client.rtm_connect():
      raise RuntimeError('unable to connect to Slack')
    return self

  def __exit__(self, *args):
    pass

  def read(self, poll_period=1):
    while True:
      for event in self.slack_client.rtm_read():
        if event['type'] == 'message':
          logger.debug('got message: {}'.format(event))
          thread = get_or_create(self.db_session, Thread, palegreendot_id=event['channel'], defaults={'name': 'Slack channel '+event['channel']})
          speaker = get_or_create(self.db_session, Person, palegreendot_id=event['user'], defaults={'name': 'Slack user '+event['user']})
          return Message(
            time=dt.datetime.now(),
            thread=thread,
            speaker=speaker,
            content=event['text'])
      time.sleep(poll_period)

  def send(self, message):
    self.slack_client.api_call(
      'chat.postMessage',
      channel=message.thread.palegreendot_id,
      text=message.content,
      as_user=True)
