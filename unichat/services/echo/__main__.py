import os
import sys
import argparse
import logging
import threading
import json

import sqlalchemy as sql
import unichat

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', action='store_true')
parser.add_argument('database')
args = parser.parse_args()

if args.verbose:
  logging.basicConfig(level=logging.DEBUG)
  logging.debug('running in verbose mode')

engine = sql.create_engine('sqlite:///'+args.database)
unichat.RelationBase.metadata.create_all(engine)
make_session = sql.orm.scoped_session(sql.orm.sessionmaker(bind=engine))

client = unichat.services.echo.Client(make_db_session=make_session)

def send_forever():
  for line in sys.stdin:
    message = unichat.Message.from_json_object(json.loads(line))
    session = make_session(); session.add(message); session.commit()
    client.send_message(message)
def receive_forever():
  print('hi', file=sys.stderr)
  for message in client.read_messages():
    print(message, file=sys.stderr)
    print(json.dumps(message.to_json_object()))
    sys.stdout.flush()

t1 = threading.Thread(target=send_forever); t1.daemon = True; t1.start()
t2 = threading.Thread(target=receive_forever); t2.daemon = True; t2.start()

import time
while True: time.sleep(9999)
