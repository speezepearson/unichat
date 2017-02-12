import datetime as dt
import time
import threading
import subprocess
import tempfile
import os
import json

import sqlalchemy

import unichat

def assert_response_equals(process, message_in, expected_message_out):
  process.stdin.write((json.dumps(message_in.to_json_object())).encode())
  process.stdin.flush()
  s = process.stdout.readline()
  print(repr(s))
  message_out = unichat.Message.from_json_object(json.loads(s.decode()))
  assert message_out.time == expected_message_out.time
  assert message_out.thread_name == expected_message_out.thread_name
  assert message_out.speaker_name == expected_message_out.speaker_name
  assert message_out.content == expected_message_out.content

def test_write_and_read_with_subprocess_client(tmpdir):
  expected_message = unichat.Message(time=dt.datetime.now(), thread_name='test thread', speaker_name='test person', content='test content')
  with unichat.services.SubprocessClient(['cat'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as client:
    client.send_message(expected_message)
    response = client.read_message()

  assert response.time == expected_message.time
  assert response.thread_name == expected_message.thread_name
  assert response.speaker_name == expected_message.speaker_name
  assert response.content == expected_message.content


def test_echo_subprocess_client(tmpdir):
  now = dt.datetime.now()

  message = unichat.Message(time=now, thread_name='test thread', speaker_name='test person', content='test content')
  expected_response = unichat.Message(time=now+dt.timedelta(seconds=1), thread_name='test thread echoed', speaker_name='test person echoed', content='test content echoed')

  with unichat.services.SubprocessClient(['python', '-m', 'unichat.services.echo', '--verbose', str(tmpdir.join('temp.db'))], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as client:
    client.send_message(message)
    response = client.read_message()

  assert response.time == message.time + dt.timedelta(seconds=1)
  assert response.thread_name == message.thread_name + ' echoed'
  assert response.speaker_name == message.speaker_name + ' echoed'
  assert response.content == message.content + ' echoed'
