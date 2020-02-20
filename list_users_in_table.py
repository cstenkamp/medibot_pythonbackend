import socket
import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from userdb import User, UserSession, UserSentiment


hostname = socket.gethostname()
if hostname == 'chris-ThinkPad-E480':
    sqlite_path = 'sqlite:////home/chris/Documents/UNI/sem_13/conversational_agents/project/db/user_states.db'
else:
    sqlite_path = 'sqlite:////var/www/medibot_pythonbackend/db/user_states.db'

engine = create_engine(sqlite_path)
Session = sessionmaker(bind=engine)
session = Session()


def parse_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--showsentiment', dest='showsentiment', default=False, help='To show sentiment', action='store_true')
    return parser.parse_args()
########################################################################################################################

def main():
    args = parse_command_line_args()
    if args.showsentiment:
        for row in session.query(User).all():
            create_sentiment_graph(row.name)
    else:
        list_tables()



def list_tables():
    print("Tables: ")
    print(engine.table_names())
    print()

    print("Users, Sessions & Sentiments:")
    for row in session.query(User).all():
        print(row)
        print(" Sessions:")
        for sess in session.query(UserSession).filter(UserSession.user == row.name).all():
            print("  ", sess)
        print(" Sentiments:")
        for sent in session.query(UserSentiment).filter(UserSentiment.user == row.name).all():
            print("  ", sent)




if __name__ == '__main__':
    main()