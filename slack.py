import time
import datetime as dt
import logging
import slackclient
from . import Message

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)

def iter_messages(client, get_username_from_id, get_channelname_from_id, poll_period=1):
  while True:
    for event in client.rtm_read():
      if event['type'] == 'message':
        logger.debug('got message: {}'.format(event))
        yield Message(
          time=dt.datetime.now(),
          thread=get_channelname_from_id(event['channel']),
          speaker=get_username_from_id(event['user']),
          content=event['text'])
    time.sleep(poll_period)

def send_messages(messages, client, get_channelid_from_name):
  for message in messages:
    client.api_call(
      'chat.postMessage',
      channel=get_channelid_from_name(message.thread),
      text=message.content,
      as_user=True)
