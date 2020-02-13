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


def create_user(name, sessionid):
    db.create_all()
    user = User.query.filter(User.name==name).one_or_none()
    if user != None:
        return None
    else:
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        store_usersession(name, sessionid)
        return User


def load_user(name, sessionid):
    db.create_all()
    user = User.query.filter(User.name==name).one_or_none()
    if user:
        store_usersession(name, sessionid)
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
        return user, True


############################################################################################################

class UserSession(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(30), nullable=False)
    starttime = db.Column(db.DateTime, nullable=False)
    sessionid = db.Column(db.String(200), unique=True, nullable=False)
    sessionlength = db.Column(db.Integer)

    def __init__(self, user, sessionid):
        self.user = user
        self.sessionid = sessionid
        self.starttime = datetime.now()

    def __repr__(self):
        return "<Session(user='%s', starttime='%s', length='%s', id='%s')>" % (self.user, str(self.starttime), str(self.sessionlength), self.sessionid)

def store_usersession(user, sessionid):
    db.create_all()
    if UserSession.query.filter(UserSession.sessionid == sessionid).one_or_none():
        return
    sess = UserSession(user=user, sessionid=sessionid)
    db.session.add(sess)
    db.session.commit()
    return sess


############################################################################################################

class UserSentiment(db.Model):
    __tablename__ = 'sentiments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(30), nullable=False)
    recordtime = db.Column(db.DateTime, nullable=False)
    sentiment = db.Column(db.String(30), nullable=False)
    strength = db.Column(db.Integer, nullable=False)
    is_initial = db.Column(db.Integer, nullable=False)

    def __init__(self, user, sentiment, strength, is_initial=True):
        self.user = user
        self.sentiment = sentiment
        self.strength = strength
        self.recordtime = datetime.now()
        self.is_initial = 1 if is_initial else 0

    def __repr__(self):
        if self.is_initial:
            return "<InitialSentiment(user='%s', recordtime='%s', sentiment='%s', strength='%s')>" % (self.user, str(self.recordtime), self.sentiment, str(self.strength))
        else:
            return "<FinalSentiment(user='%s', recordtime='%s', sentiment='%s', strength='%s')>" % (self.user, str(self.recordtime), self.sentiment, str(self.strength))


def store_sentiment(user, sentiment, strength, is_intitial=True):
    db.create_all()
    sent = UserSentiment(user=user, sentiment=sentiment, strength=strength, is_initial=is_intitial)
    db.session.add(sent)
    db.session.commit()
    return sent
