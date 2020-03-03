import socket
import tempfile
from os.path import join, basename, abspath
from math import pi
import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from matplotlib import pyplot as plt

import userdb
import settings

PRIVATE_HOSTNAMES = ['chris-ThinkPad-E480', 'AronLaptop']
MERGE_DAYS = True

SENTIMENTS = ['energized-neutral',
              'energized-pleasant',
              'neutral-pleasant',
              'calm-pleasant',
              'calm-neutral',
              'calm-unpleasant',
              'neutral-unpleasant',
              'energized-unpleasant'
              ]
# TODO die per API von den entities ziehen https://dialogflow.com/docs/reference/v2-auth-setup

sentiment = lambda x: -1 if 'unpleasant' in x else 1 if 'pleasant' in x and not 'unpleasant' in x else 0
energized = lambda x: 1 if 'energized' in x else -1 if 'calm' in x else 0

hostname = socket.gethostname()
if hostname in PRIVATE_HOSTNAMES:
    sqlite_path = 'sqlite:///'+join(abspath('.'), 'db', 'user_states.db')
else:
    EMOTION_IMG_BASE_DIR = settings.EMOTION_BASE_DIR
    sqlite_path = 'sqlite:///' + settings.DBPATH + settings.DBNAME

engine = create_engine(sqlite_path)
Session = sessionmaker(bind=engine)
session = Session()


def create_sentiment_graph(for_user, for_days='all', show_initial=True, show_starplot=True): #show_initial kann True, False, 2 sein. bei 2 zeigt's alle.

    sentiment_dict = {key: [] for key in SENTIMENTS}
    sentiment_verlauf = []
    energized_verlauf = []
    date_verlauf = []

    if for_days == 'all':
        qry = session.query(userdb.UserSentiment).filter(userdb.UserSentiment.user==for_user, userdb.UserSentiment.is_initial==int(show_initial)).all() if show_initial < 2 else \
                session.query(userdb.UserSentiment).filter(userdb.UserSentiment.user==for_user).all()
    else:
        geqthan_date = (datetime.today() - timedelta(days=int(for_days))).date()
        qry = session.query(userdb.UserSentiment).filter(userdb.UserSentiment.recordtime >= geqthan_date, userdb.UserSentiment.user==for_user, userdb.UserSentiment.is_initial==int(show_initial)).all() if show_initial < 2 else \
                session.query(userdb.UserSentiment).filter(userdb.UserSentiment.recordtime >= geqthan_date, userdb.UserSentiment.user==for_user).all()
    for sent in qry:
        # print(sent.recordtime.date(), sent.recordtime.date() >= (datetime.today() - timedelta(days=int(for_days))).date())
        sentiment_dict[sent.sentiment].append(sent.strength)
        sentiment_verlauf.append(sent.strength * sentiment(sent.sentiment))
        energized_verlauf.append(sent.strength * energized(sent.sentiment))
        date_verlauf.append(sent.recordtime)

    if show_starplot:
        fig, ax = make_starplot(sentiment_dict, show_initial)
    else:
        fig, ax = make_histplot(date_verlauf, sentiment_verlauf, energized_verlauf, MERGE_DAYS, show_initial)

    filename = tempfile.mkstemp('.png')[1]
    #TODO den nicht als wert haben, und irgendwie für sicherheit hier sorgen, muss leider http sein
    if hostname in PRIVATE_HOSTNAMES:
        plt.show()
    else:
        os.makedirs(EMOTION_IMG_BASE_DIR, exist_ok=True)
        filename = join(EMOTION_IMG_BASE_DIR, basename(filename))
        plt.savefig(filename)
        plt.close(fig)
    return filename


def merge_indiv_days(date_verlauf, res_verlauf):
    res_dict = {}
    for elem in [(i[0].date(), i[1]) for i in zip(date_verlauf, res_verlauf)]:
        try:
            res_dict[elem[0]].append(elem[1])
        except:
            res_dict[elem[0]] = [elem[1]]
    return res_dict


def make_histplot(date_verlauf, sentiment_verlauf, energized_verlauf, merge_days, show_initial):
    if len(date_verlauf) < 10:
        merge_days = False
    if merge_days:
        tmp = {key: sum(val) / len(val) for key, val in merge_indiv_days(date_verlauf, sentiment_verlauf).items()}
        x_axis = list(tmp.keys()); y_axis = list(tmp.values())
        tmp = {key: sum(val) / len(val) for key, val in merge_indiv_days(date_verlauf, sentiment_verlauf).items()}
        y_axis2 = list(tmp.values())
    else:
        x_axis = date_verlauf; y_axis = sentiment_verlauf; y_axis2 = energized_verlauf

    fig, ax = plt.subplots(1, 1)
    ax.plot(range(len(y_axis)), y_axis, color='blue', label='sentiment')
    ax.plot(range(len(y_axis2)), y_axis2, color='red', linestyle='--', label='energy')
    ax.plot(range(len(y_axis)), [0]*len(y_axis), color='black', linestyle=':', label='neutral')
    ax.set(ylim=(-8, 8), xticks=range(len(y_axis)))
    ax.set_xticklabels([str(i)[:str(i).find('.') if str(i).find('.') > 0 else None] for i in x_axis], rotation=25, ha='right')
    ax.set(ylabel='Rating (Daily Average)' if MERGE_DAYS else 'Rating',
           title='History of '+('initial' if show_initial==1 else 'final' if show_initial==0 else 'overall')+' Sentiment and Energy')
    ax.legend()
    return fig, ax



def make_starplot(sentiment_dict, show_initial):

    averages = {key: sum(val)/len(val) if len(val) > 0 else 1  for key, val in sentiment_dict.items()}
    attnr = len(SENTIMENTS)
    angles = [n / float(attnr) * 2 * pi for n in range(attnr)]
    angles += angles[:1]
    angles = angles[:-1]

    val = list(averages.values())
    fig, ax = plt.subplots(1, subplot_kw = dict(polar = True))
    #ax = plt.subplot(111, polar=True)
    plt.xticks(angles[:], SENTIMENTS)

    ax.plot(angles+angles[0:1], val+val[0:1])
    ax.fill(angles, val, 'teal', alpha=0.2)
    ax.set(ylim=[0,7], title="Average "+('initial' if show_initial==1 else 'final' if show_initial==0 else 'overall')+" sentiment")

    return fig, ax

def main():
    create_sentiment_graph('chris', 19)


if __name__ == '__main__':
    main()
