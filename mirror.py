import argparse
import csv
import os
import slackclient
import unichat

parser = argparse.ArgumentParser()
parser.add_argument('threads_csv')
parser.add_argument('people_csv')
args = parser.parse_args()

def squash_name(name):
  words = [w for w in name.split(' ') if w]
  return '{first} {last_initials}'.format(
    first=words[0],
    last_initials=''.join(w[0] for w in words[1:]))

for varname in ['SALAZAR_SLACK_TOKEN', 'SALAZAR_FB_EMAIL', 'SALAZAR_FB_PASSWORD']:
  if not os.environ.get(varname):
    raise RuntimeError('{} must be set in environment'.format(varname))

client = slackclient.SlackClient(os.environ['SALAZAR_SLACK_TOKEN'])
if not client.rtm_connect():
  logger.error("Connection failed. Invalid Slack token or bot ID?")
  exit(1)

def lookup(result_key, dicts, query_key, query_value, default=None):
  for d in dicts:
    if d[query_key] == query_value:
      return d[result_key]
  return default

people = list(csv.DictReader(open(args.people_csv)))
threads = list(csv.DictReader(open(args.threads_csv)))
print(people)
print(threads)

slack_messages = unichat.slack.iter_messages(
  client,
  get_username_from_id=(lambda id: lookup('name', people, 'slack_id', id, default=('(???)({})'.format(id)))),
  get_channelname_from_id=(lambda id: lookup('name', threads, 'slack_id', id, default=('(???)({})'.format(id)))))
def _log(xs):
  for x in xs:
    print('In Slack:', x)
    yield x
slack_messages = _log(slack_messages)
slack_messages = (m._replace(content='{}: {}'.format(squash_name(m.speaker), m.content)) for m in slack_messages if m.speaker != 'salazar')

fb_messages = unichat.fb.iter_messages(
  get_username_from_id=(lambda id: lookup('name', people, 'fb_id', id, default=('(???)({})'.format(id)))),
  get_channelname_from_id=(lambda id: lookup('name', threads, 'fb_id', id, default=('(???)({})'.format(id)))))
def _log(xs):
  for x in xs:
    print('In FB:', x)
    yield x
fb_messages = _log(fb_messages)
fb_messages = (m._replace(content='`{}` {}'.format(squash_name(m.speaker), m.content)) for m in fb_messages if m.speaker != 'salazar')


def dump_slack_to_fb():
  unichat.fb.send_messages(
    slack_messages,
    get_channelid_from_name=(lambda name: lookup('fb_id', threads, 'name', name)))
def dump_fb_to_slack():
  unichat.slack.send_messages(
    fb_messages,
    client,
    get_channelid_from_name=(lambda name: lookup('slack_id', threads, 'name', name)))

import threading
threading.Thread(target=dump_slack_to_fb).start()
dump_fb_to_slack()
