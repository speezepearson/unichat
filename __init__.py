import csv
import collections

Message = collections.namedtuple('Message', ['time', 'thread', 'speaker', 'content'])

def write_messages_to_csv(messages, file, header=True):
  writer = csv.DictWriter(file, fieldnames=Message._fields)
  if header:
    writer.writeheader()
  for message in messages:
    writer.writerow(message._asdict())
  file.flush()
def read_messages_from_csv(file, header=True):
  reader = csv.reader(file)
  if header:
    next(reader)
  return (Message(*row) for row in reader)

from . import slack, fb
