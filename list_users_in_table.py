import socket
import argparse
import tempfile
from os.path import join, basename

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from matplotlib import pyplot as plt

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


def create_sentiment_graph(for_user, show_initial=True): #show_initial kann True, False, 2 sein. bei 2 zeigt's alle.
    SENTIMENTS = ['happy', 'stressed', 'relaxed', 'lazy', 'bad'] #TODO die per API von den entities ziehen https://dialogflow.com/docs/reference/v2-auth-setup
    sentiment_dict = {key: [] for key in SENTIMENTS}
    qry = session.query(UserSentiment).filter(UserSentiment.user==for_user, UserSentiment.is_initial==int(show_initial)).all() if show_initial < 2 else \
            session.query(UserSentiment).filter(UserSentiment.user==for_user).all()
    #TODO im frontend gibt man da die letzten Tage an, das noch machen
    for sent in qry:
        try:
            sentiment_dict[sent.sentiment].append(sent.strength)
        except KeyError:
            sentiment_dict[sent.sentiment] = [sent.strength]
    averages = {key: sum(val)/len(val) if len(val) > 0 else 0 for key, val in sentiment_dict.items()}

    fig, ax = plt.subplots(1)
    ax.bar(averages.keys(), averages.values(), 0.6, color='b')
    ax.set(ylim=[0,7], title="Average "+("initial" if show_initial else "final")+" sentiment")
    filename = tempfile.mkstemp('.png')[1]
    filename = join('/var/www/html/emotion_imgs', basename(filename)) #TODO den nicht als wert haben, und irgendwie für sicherheit hier sorgen, muss leider http sein
    plt.savefig(filename)
    plt.close(fig)
    return filename


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