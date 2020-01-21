import sys
sys.path.append("pydevd-pycharm.egg")
import pydevd_pycharm
pydevd_pycharm.settrace('31.17.253.171', port=12345, stdoutToServer=True, stderrToServer=True)

############################### externe imports ####################################
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json

####################################################################################

app = Flask(__name__) #that's what's imported in the wsgi file
app.config.from_object(__name__)
app.config.update(
    SESSION_COOKIE_NAME = 'session_medibot',
    SESSION_COOKIE_PATH = '/medibot/'
)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sql  ite:///'+settings.DBPATH+settings.DBNAME
# db = SQLAlchemy(app)

######################## interne imports, NACH creation der db #####################
# from bothelper import handle_update, send_message

####################################################################################

@app.route("/", methods=["POST", "GET"])
def update():
    if request.method == 'POST':
        update = request.data.decode("utf8")
        update = json.loads(update)
        print("====================================== REQUEST.DATA ======================================")
        print(request.data)
        print("====================================== UPDATE ======================================")
        print(update)
        # handle_update(update)
        return "" #"" = 200 responsee
    else:
        return "This page is reserved for the MediBot (/)"


####################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0")