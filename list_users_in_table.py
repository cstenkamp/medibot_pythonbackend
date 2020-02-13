from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from userdb import User

engine = create_engine('sqlite:////var/www/medibot_pythonbackend/db/user_states.db')
Session = sessionmaker(bind=engine)
session = Session()

print (engine.table_names())
for row in session.query(User).all():
    print(row)