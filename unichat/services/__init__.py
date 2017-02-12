import abc

class ClientBase(metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def read_message(self):
    pass

  @abc.abstractmethod
  def send_message(self):
    pass


  def connect(self):
    pass
  def disconnect(self):
    pass

  def __enter__(self):
    self.connect()
    return self
  def __exit__(self, exc_type, exc_value, traceback):
    self.disconnect()

  def read_messages(self):
    while True:
      yield self.read_message()

  def send_messages(self, messages):
    for message in messages:
      self.send_message(message)


from . import facebook, slack, echo
from .subprocessclient import SubprocessClient
