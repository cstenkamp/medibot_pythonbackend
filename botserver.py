import sys
sys.path.append("pydevd-pycharm.egg")
import pydevd_pycharm
print("botserver started")

############################### externe imports ####################################
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import requests, curlify
import settings

####################################################################################

application = Flask(__name__) #that's what's imported in the wsgi file
application.config.from_object(__name__)
application.config.update(
    SESSION_COOKIE_NAME = 'session_medibot',
    SESSION_COOKIE_PATH = '/medibot/'
)

print('Database file', 'sqlite:///'+settings.DBPATH+settings.DBNAME)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + settings.DBPATH + settings.DBNAME
db = SQLAlchemy(application)

######################## now that the app exists, we can connect the debugger! #####################
# # #https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html
# # #https://stackoverflow.com/questions/47581248/how-to-remote-debug-flask-request-behind-uwsgi-in-pycharm?rq=1

@application.before_first_request
def before_first_request():
    pass
    # pydevd_pycharm.settrace('localhost', port=12346, stdoutToServer=True, stderrToServer=True)
    # print('debugger connected')


######################## interne imports, NACH creation der db #####################
# from bothelper import handle_update, send_message

import handle_intent
####################################################################################

# wenn das mit den routen nicht hinhaut:
#   -https://stackoverflow.com/questions/7558249/nginx-configuration-for-static-sites-in-root-directory-flask-apps-in-subdirecto
#   -https://stackoverflow.com/questions/18967441/add-a-prefix-to-all-flask-routes
#   -https://www.nginx.com/blog/creating-nginx-rewrite-rules/#server_name
@application.route("/", methods=["POST", "GET"])
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

@application.route("/helloworld")
def hello():
    return """
        Hello World!<br /><br />
        <a href="/">Back to index</a>
    """


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
    application.run(host="0.0.0.0")
