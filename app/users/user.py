from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from extensions import db

class User(db.Model, UserMixin):

  __tablename__ = "user"
  def __repr__(self):
    return '<User %r>' % (self.user_name)

  id             = db.Column(db.Integer, primary_key = True)
  user_name      = db.Column(db.String(32),  index = True, unique = True, nullable=False)
  recent_first   = db.Column(db.String(32))
  recent_second  = db.Column(db.String(32))
  recent_results = db.Column(db.PickleType)

  # User Password
  _password = db.Column('password', db.String(32), nullable=False)

  def get_password(self):
    return self._password

  def set_password(self, password):
    self._password = generate_password_hash(password)

  password = db.synonym('_password', descriptor = property(get_password, set_password))

  def check_password(self, password):
    if self.password is None:
      return False
    return check_password_hash(self.password, password)

  @classmethod
  def authenticate(cls, user_name, password):
    user = User.query.filter(db.or_(User.user_name == user_name)).first()

    if user:
      authenticated = user.check_password(password)
    else:
      authenticated = False
    return user, authenticated

  @classmethod
  def user_name_exists(cls, user_name):
    return db.session.query(db.exists().where(User.user_name==user_name)).scalar()
