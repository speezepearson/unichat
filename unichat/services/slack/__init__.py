import time
import datetime as dt
import logging
import slackclient
from sqlalchemy_bonus import session_context, get_or_create
from .. import ClientBase
from ... import Message, Thread, Person

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Client(ClientBase):
  def __init__(self, slack_client, make_db_session):
    self.slack_client = slack_client
    self.make_db_session = make_db_session

  def connect(self):
    if not self.slack_client.rtm_connect():
      raise RuntimeError('unable to connect to Slack')

  def read_message(self, poll_period=1):
    while True:
      for event in self.slack_client.rtm_read():
        if event['type'] == 'message':
          logger.debug('got message: {}'.format(event))

          with session_context(self.make_db_session()) as session:
            thread = get_or_create(session, Thread, palegreendot_id=event['channel'], defaults={'name': 'Slack channel '+event['channel']})
            speaker = get_or_create(session, Person, palegreendot_id=event['user'], defaults={'name': 'Slack user '+event['user']})
            m = Message(
              time=dt.datetime.now(),
              thread=thread,
              speaker=speaker,
              content=event['text'])
            session.add(m)
            return m
        time.sleep(poll_period)

  def send_message(self, message):
    self.slack_client.api_call(
      'chat.postMessage',
      channel=message.thread.palegreendot_id,
      text=message.content,
      as_user=True)
