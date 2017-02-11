import os
import sys
import argparse

import slackclient
import sqlalchemy as sql
import unichat

for varname in ['SLACK_API_TOKEN']:
  if not os.environ.get(varname):
    raise RuntimeError('{} must be set in environment'.format(varname))

parser = argparse.ArgumentParser()
parser.add_argument('database')
args = parser.parse_args()

engine = sql.create_engine('sqlite:///'+args.database)
unichat.RelationBase.metadata.create_all(engine)
make_session = sql.orm.scoped_session(sql.orm.sessionmaker(bind=engine))

def make_client():
  return unichat.services.slack.Client(
    slack_client=slackclient.SlackClient(os.environ['SLACK_API_TOKEN']),
    make_db_session=make_session)

import threading, sys, json
def send_forever():
  with make_client() as client:
    for line in sys.stdin:
      message = unichat.Message.from_json_object(json.loads(line))
      session = make_session(); session.add(message); session.commit()
      client.send_message(message)
def receive_forever():
  with make_client() as client:
    for message in client.read_messages():
      print(json.dumps(message.to_json_object()))
      sys.stdout.flush()

threading.Thread(target=send_forever).start()
threading.Thread(target=receive_forever).start()
