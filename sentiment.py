import socket
import tempfile
from os.path import join, basename, abspath
from math import pi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from userdb import UserSentiment #geht nicht, dann hat python circular imports
from matplotlib import pyplot as plt

PRIVATE_HOSTNAMES = ['chris-ThinkPad-E480', 'AronLaptop']

hostname = socket.gethostname()
if hostname in PRIVATE_HOSTNAMES:
    sqlite_path = 'sqlite:///'+join(abspath('.'), 'db', 'user_states.db')
else:
    sqlite_path = 'sqlite:////var/www/medibot_pythonbackend/db/user_states.db'

engine = create_engine(sqlite_path)
Session = sessionmaker(bind=engine)
session = Session()


def create_sentiment_graph(for_user, show_initial=True): #show_initial kann True, False, 2 sein. bei 2 zeigt's alle.
    SENTIMENTS = [ 'energized-neutral',
                   'energized-pleasant',
                   'neutral-pleasant',
                   'calm-pleasant',
                   'calm-neutral',
                   'calm-unpleasant',
                   'neutral-unpleasant',
                   'energized-unpleasant'
                   ]
    #TODO die per API von den entities ziehen https://dialogflow.com/docs/reference/v2-auth-setup
    sentiment_dict = {key: [] for key in SENTIMENTS}
    qry = session.query(UserSentiment).filter(UserSentiment.user==for_user, UserSentiment.is_initial==int(show_initial)).all() if show_initial < 2 else \
            session.query(UserSentiment).filter(UserSentiment.user==for_user).all()
    #TODO im frontend gibt man da die letzten Tage an, das noch machen
    for sent in qry:
        try:
            sentiment_dict[sent.sentiment].append(sent.strength)
        except KeyError:
            sentiment_dict[sent.sentiment] = [sent.strength]
    averages = {key: sum(val)/len(val) if len(val) > 0 else 1  for key, val in sentiment_dict.items()}
    attnr = len(SENTIMENTS)
    angles = [n / float(attnr) * 2 * pi for n in range(attnr)]
    angles += angles[:1]
    angles = angles[:-1]

    val = list(averages.values())
    fig, ax = plt.subplots(1, subplot_kw = dict(polar = True))
    #ax = plt.subplot(111, polar=True)
    plt.xticks(angles[:], SENTIMENTS)

    ax.plot(angles, val)
    ax.fill(angles, val, 'teal', alpha=0.2)
    ax.set(ylim=[0,7], title="Average "+("initial" if show_initial else "final")+" sentiment")

    filename = tempfile.mkstemp('.png')[1]
    filename = join('/var/www/html/emotion_imgs', basename(filename))
    #TODO den nicht als wert haben, und irgendwie für sicherheit hier sorgen, muss leider http sein
    if hostname in PRIVATE_HOSTNAMES:
        plt.show()
    else:
        plt.savefig(filename)
        plt.close(fig)
    return filename


def main():
    create_sentiment_graph('chris')


if __name__ == '__main__':
    main()
