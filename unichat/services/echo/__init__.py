import time
import datetime as dt
import logging
import queue
from sqlalchemy_bonus import session_context, get_or_create
from .. import ClientBase
from ... import Message, Thread, Person

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Client(ClientBase):
  def __init__(self, make_db_session):
    self.make_db_session = make_db_session
    self.message_queue = queue.Queue()

  def read_message(self):
    logger.debug('waiting for message...')
    result = self.message_queue.get()
    logger.info('got message: {}'.format(result))
    return result

  def send_message(self, message):
    echoed_message = Message(
      time=message.time + dt.timedelta(seconds=1),
      thread_name=message.thread_name+' echoed',
      speaker_name=message.speaker_name+' echoed',
      content=message.content+' echoed')
    logger.info('sending message: {}'.format(echoed_message))
    self.message_queue.put(echoed_message)
