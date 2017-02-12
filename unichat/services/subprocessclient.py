import subprocess
import json
from .. import Message
from . import ClientBase

class SubprocessClient(ClientBase):
  def __init__(self, *popen_args, **popen_kwargs):
    self.process = None
    self.popen_args = popen_args
    self.popen_kwargs = popen_kwargs

  def connect(self):
    self.process = subprocess.Popen(*self.popen_args, **self.popen_kwargs)
  def disconnect(self):
    self.process.stdin.close()
    self.process.stdout.close()
    self.process.kill()
    self.process.wait()
    print('disconnected')

  def read_message(self):
    line = self.process.stdout.readline()
    return Message.from_json_object(json.loads(line.decode()))
  def send_message(self, message):
    payload = json.dumps(message.to_json_object())
    self.process.stdin.write(payload.encode() + b'\n')
    self.process.stdin.flush()
