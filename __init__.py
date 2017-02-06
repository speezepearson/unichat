import sqlalchemy as sql
import sqlalchemy.ext.declarative

RelationBase = sqlalchemy.ext.declarative.declarative_base()

class Message(RelationBase):
  __tablename__ = 'Message'
  id = sql.Column(sql.Integer, primary_key=True)
  time = sql.Column(sql.DateTime)
  thread_name = sql.Column(sql.String, sql.ForeignKey('Thread.name'))
  speaker_name = sql.Column(sql.String, sql.ForeignKey('Person.name'))
  content = sql.Column(sql.String)

  thread = sql.orm.relationship('Thread')
  speaker = sql.orm.relationship('Person')

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
