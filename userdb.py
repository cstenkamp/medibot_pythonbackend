from botserver import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createdate = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return "<User(id='%i', name='%s', created at='%s')>" % (self.id, self.name, str(self.createdate))

    def __init__(self, name):
        self.name = name
        self.createdate = datetime.now()


def create_user(name):
    db.create_all()
    user = User.query.filter(User.name==name).one_or_none()
    if user != None:
        return None
    else:
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return User


def load_user(name):
    db.create_all()
    user = User.query.filter(User.name==name).one_or_none()
    return user #user or None



def create_or_load_user(name):
    db.create_all()
    user = User.query.filter(User.name==name).one_or_none()
    if user != None:
        return user, False
    else:
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        db.session.commit()
        return user, True


