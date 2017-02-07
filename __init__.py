import datetime as dt
import sqlalchemy as sql
import sqlalchemy.ext.declarative

RelationBase = sqlalchemy.ext.declarative.declarative_base()

class Message(RelationBase):
  __tablename__ = 'Message'
  id = sql.Column(sql.Integer, primary_key=True)
  time = sql.Column(sql.DateTime)
  thread_name = sql.Column(sql.String, sql.ForeignKey('Thread.name'), nullable=False)
  speaker_name = sql.Column(sql.String, sql.ForeignKey('Person.name'), nullable=False)
  content = sql.Column(sql.String, nullable=False)

  thread = sql.orm.relationship('Thread')
  speaker = sql.orm.relationship('Person')

  def __repr__(self):
    return '<Message: {} [{}]: {}>'.format(self.speaker_name, self.thread_name, repr(self.content))

  def to_json_object(self):
    return {
      'time': self.time.strftime('%Y-%m-%d %H:%M:%S.%f'),
      'thread_name': self.thread_name,
      'speaker_name': self.speaker_name,
      'content': self.content}

  @classmethod
  def from_json_object(cls, j):
    return cls(
      time=dt.datetime.strptime(j['time'], '%Y-%m-%d %H:%M:%S.%f'),
      thread_name=j['thread_name'],
      speaker_name=j['speaker_name'],
      content=j['content'])

class Person(RelationBase):
  __tablename__ = 'Person'
  name = sql.Column(sql.String, primary_key=True)
  nickname = sql.Column(sql.String)
  fb_id = sql.Column(sql.String, unique=True)
  palegreendot_id = sql.Column(sql.String, unique=True)
  opted_into_snakechat_mention_notifications = sql.Column(sql.Boolean, default=False)

class Thread(RelationBase):
  __tablename__ = 'Thread'
  name = sql.Column(sql.String, primary_key=True)
  fb_id = sql.Column(sql.String, unique=True)
  palegreendot_id = sql.Column(sql.String, unique=True)



from . import services
