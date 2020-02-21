# # #https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html#
import sys
sys.path.append("pydevd-pycharm.egg")
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)

############################### externe imports ####################################
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import requests, curlify
import settings

####################################################################################

app = Flask(__name__) #that's what's imported in the wsgi file
app.config.from_object(__name__)
app.config.update(
    SESSION_COOKIE_NAME = 'session_medibot',
    SESSION_COOKIE_PATH = '/medibot/'
)

print('Database file', 'sqlite://'+settings.DBPATH+settings.DBNAME)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+settings.DBPATH+settings.DBNAME
db = SQLAlchemy(app)

######################## interne imports, NACH creation der db #####################
# from bothelper import handle_update, send_message

import handle_intent
####################################################################################

@app.route("/", methods=["POST", "GET"])
def update():
    if request.method == 'POST':
        update = request.data.decode("utf8")
        update = json.loads(update)
        print("====================================== REQUEST.DATA ======================================")
        #print(request.data)
        response = handle_intent.handle_intent(update['queryResult']['intent']['displayName'], update)
        # post_command('http://'+remote_addr, requestHeaders, response)
        if response:
            print("responding: ", response)
        return response
        # handle_update(update)
        return "" #"" = 200 responsee
    else:
        return "This page is reserved for the MediBot (/)"



def post_command(url, headers, content):
    reqres = requests.post(url, headers=headers, data=content)
    result = ["CURL command: "+str(curlify.to_curl(reqres.request))]
    #print("CURL command:", curlify.to_curl(reqres.request))
    if reqres.status_code != 200:
        result.append('Return code: '+str(reqres.status_code))
        result.append(reqres.text)
    else:
        if reqres.content:
            result.append(str(reqres.json()))
        else:
            result.append("Successful.")
    return result




####################################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0")