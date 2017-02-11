import os
import sys
import argparse

import sqlalchemy as sql
import unichat

for varname in ['FACEBOOK_EMAIL', 'FACEBOOK_PASSWORD']:
  if not os.environ.get(varname):
    raise RuntimeError('{} must be set in environment'.format(varname))

parser = argparse.ArgumentParser()
parser.add_argument('database')
args = parser.parse_args()

engine = sql.create_engine('sqlite:///'+args.database)
unichat.RelationBase.metadata.create_all(engine)
make_session = sql.orm.scoped_session(sql.orm.sessionmaker(bind=engine))

client = unichat.services.facebook.Client(
  email=os.environ['FACEBOOK_EMAIL'],
  password=os.environ['FACEBOOK_PASSWORD'],
  make_db_session=make_session)

import threading, sys, json
def send_forever():
  for line in sys.stdin:
    message = unichat.Message.from_json_object(json.loads(line))
    session = make_session(); session.add(message); session.commit()
    client.send_message(message)
def receive_forever():
  for message in client.read_messages():
    print(json.dumps(message.to_json_object()))
    sys.stdout.flush()

with client:
  sending_thread = threading.Thread(target=send_forever)
  receiving_thread = threading.Thread(target=receive_forever)
  sending_thread.start(); receiving_thread.start()
  sending_thread.join(); receiving_thread.join()
