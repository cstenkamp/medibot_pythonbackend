import json
from os import path
from copy import deepcopy

from sample_jsons import SAMPLE_PAYLOAD_JSON, SAMPLE_RESPONSE_JSON, SAMPLE_IMAGE_JSON
from sentiment import create_sentiment_graph
import userdb
import settings
import pandas as pd

MEDITATION_STANDARD_LENGTH = 3
STANDARD_EMOTIONSNAPSHOT_LEN = 5

argmax = lambda l: max(zip(l, range(len(l))))[1]
argmin = lambda l: min(zip(l, range(len(l))))[1]

def handle_intent(intent_name, req_json):
    if intent_name == 'meditation.start':
        return start_meditation(req_json)
    elif intent_name == 'session.login':
        return login(req_json)
    elif intent_name == 'session.register':
        return register(req_json)
    elif intent_name == 'sentiment.eval.initial':
        return store_sentiment(req_json)
    elif intent_name == 'sentiment.history':
        return show_sentiment(req_json, True)
    elif intent_name == 'sentiment.snapshot':
        return show_sentiment(req_json, False)
    elif intent_name == 'meditation.start.parametersthere':
        print()


def show_sentiment(req_json, show_hist):
    username = userdb.UserSession.query.filter(userdb.UserSession.sessionid == req_json['session']).one_or_none().user
    if req_json['queryResult']['parameters']['duration'] == '':
        duration_days = 'all' if show_hist else STANDARD_EMOTIONSNAPSHOT_LEN
    else:
        duration_dict = req_json['queryResult']['parameters']['duration']
        if duration_dict['unit'] in ['mo', 'mos']:
            duration_dict['amount'] *= 30; duration_dict['unit'] = duration_dict['unit'].replace('mo', 'day') #pandas doesn't know months v.v
        if duration_dict['unit'] in ['yr', 'yrs']:
            duration_dict['amount'] *= 365; duration_dict['unit'] = duration_dict['unit'].replace('yr', 'day') #pandas doesn't know months v.v
        duration_str = str(duration_dict['amount'])+' '+(duration_dict['unit']+'s' if not duration_dict['unit'].endswith('s') else duration_dict['unit'])
        duration_days = round(pd.to_timedelta(duration_str).total_seconds()/3600/24)
    imgpath = create_sentiment_graph(username, for_days=duration_days, show_initial=2, show_starplot=not show_hist) #TODO show_initial kann 3 verschiedene Werte haben
    imgpath = imgpath.replace(settings.EMOTION_BASE_DIR, settings.IMAGE_DOMAIN)
    if show_hist:
        if duration_days == 'all':
            return image_response(imgpath, "Here's your emotional history", 'Your emotional history with me', '<plot with your emotional history>', ['Menu'])
        else:
            return image_response(imgpath, "Here's your emotional history of the last "+str(duration_days)+' days', 'Your emotional history of the last '+str(duration_days)+' days', '<plot with your emotional history>', ['Menu'])
    else:
        return image_response(imgpath, "Here's your emotional state of the last "+str(duration_days)+' days', 'Your emotional state of the last '+str(duration_days)+' days', '<starplot with your emotional state>', ['Menu'])


def image_response(imgpath, textresponse='Here is your image', title='', accessibilitytext='', suggestions=None):
    resp = SAMPLE_IMAGE_JSON
    resp['payload']['google']['richResponse']['items'][1]['basicCard']['image']['url'] = imgpath
    if textresponse:
        resp['payload']['google']['richResponse']['items'][0]['simpleResponse']['textToSpeech'] = textresponse
    if title:
        resp['payload']['google']['richResponse']['items'][1]['basicCard']['title'] = title
    if accessibilitytext:
        resp['payload']['google']['richResponse']['items'][1]['basicCard']['accessibilityText'] = accessibilitytext
    if suggestions:
        resp['payload']['google']['richResponse']['suggestions'] = [{'title': i} for i in suggestions]
    return resp



def standard_response(text, suggestions=None):
    resp = deepcopy(SAMPLE_RESPONSE_JSON)
    resp['payload']['google']['richResponse']['items'][0]['simpleResponse']['textToSpeech'] = text
    if suggestions:
        resp['payload']['google']['richResponse']['suggestions'] = [{'title': i} for i in suggestions]
    return resp



def store_sentiment(req_json):
    assert req_json['queryResult']['allRequiredParamsPresent']
    print("storing sentiment")
    #username = req_json['queryResult']['parameters']['username'].lower() #TODO warum ist er einfach gone?!
    username = userdb.UserSession.query.filter(userdb.UserSession.sessionid == req_json['session']).one_or_none().user

    strength = req_json['queryResult']['parameters']['sentiment-strength']
    sentiment = req_json['queryResult']['parameters']['sentiment']
    if req_json['queryResult']['intent']['displayName'] == 'sentiment.eval.initial':
        userdb.store_sentiment(username, sentiment, strength, is_intitial=True)
    else:
        userdb.store_sentiment(username, sentiment, strength, is_initial=False)

    return standard_response("Okay, I noted down that feeling.", ["Menu", "Meditation"])  #TODO die standard-suggestion-chips irgendwo eher haben




def login(req_json):
    print('Logging in.')
    username = req_json['queryResult']['parameters']['username'].lower()
    user = userdb.load_user(username, req_json['session'])
    if not user:
        print("This user doesn't exist")
        return {'outputContexts': [{'name': req_json['session']+'/contexts/login-incomplete', "lifespanCount": 5, 'parameters': req_json['queryResult']['parameters']}], "followupEventInput": {"name": "login-failed", "languageCode": "en"}}
    print("This user exists")
    # result = {'outputContexts': req_json['queryResult']['outputContexts'], 'parameters': req_json['queryResult']['parameters'], "followupEventInput": {"name": "login-success", "languageCode": "en"}}
    result = {'outputContexts': [], "followupEventInput": {"name": "login-success", "languageCode": "en"}}
    result['outputContexts'].append({'name': req_json['session']+'/contexts/login-incomplete', "lifespanCount": 5, 'parameters': req_json['queryResult']['parameters']})
    # result = {"followupEventInput": {"name": "login-success", "languageCode": "en"}}
    print(result)
    return result


def register(req_json):
    print("Registering")
    username = req_json['queryResult']['parameters']['username'].lower()
    user = userdb.create_user(username, req_json['session'])
    if not user:
        print("This username exists already!")
        return {'outputContexts': [{'name': req_json['session']+'/contexts/login-incomplete', "lifespanCount": 5, 'parameters': req_json['queryResult']['parameters']}], "followupEventInput": {"name": "register-failed", "languageCode": "en"}}
    else:
        print("success.")

        return {'outputContexts': [{'name': req_json['session']+'/contexts/login-incomplete', "lifespanCount": 5, 'parameters': req_json['queryResult']['parameters']}], "followupEventInput": {"name": "register-success", "languageCode": "en"}}


def start_meditation(req_json):
    assert get_username(req_json) # TODO ne andere response zurückgeben falls kein User
    #TODO: wenn json['queryResult']['parameters']['meditation-length'] gesetzt ist erst in x minuten

    try:
        parameters = {**[i for i in req_json['alternativeQueryResults'][0]['outputContexts'] if i['name'].endswith('meditation-active')][0]['parameters'], **{key: val for key, val in req_json['queryResult']['parameters'].items() if val}} # Why the fuck do you forget it Dialogflow?!
    except:
        parameters = req_json['queryResult']['parameters']

    if 'allRequiredParamsPresent' in req_json['queryResult'] and req_json['queryResult']['allRequiredParamsPresent']: #nur nicht da wenn man für slotfilling macht
        print('starting meditation...')
    else:
        if not parameters['meditation-type']:
            return '' #typ von dialogflow regeln lassen

    meditation_type = parameters['meditation-type']
    meditation_length = parameters['meditation-length']
    if not meditation_length:
        with open(path.join(settings.FILES_ROOT_DIR, 'meditations.json')) as json_file:
            meditation_data = json.load(json_file)
        correct_type = meditation_data[meditation_type]
        lens = sorted([int(i) for i in correct_type.keys()])
        resp = standard_response('How long a meditation did you have in mind?', [str(i)+' minutes' for i in lens])
        resp['outputContexts'] = [{'name': req_json['session']+'/contexts/meditation-active', "lifespanCount": 5, 'parameters': {key: val for key, val in parameters.items() if key != 'meditation-length'}}]
        return resp

    resp_meditation = SAMPLE_PAYLOAD_JSON
    where_media = [num for num, i in enumerate(resp_meditation['payload']['google']['richResponse']['items']) if
                   'mediaResponse' in i.keys()][0]
    with open(path.join(settings.FILES_ROOT_DIR, 'meditations.json')) as json_file:
        meditation_data = json.load(json_file)
    correct_type = meditation_data[meditation_type]
    lens = sorted([int(i) for i in correct_type.keys()])

    if meditation_length not in lens:
        len_diffs = [abs(i-meditation_length) for i in lens]
        if len_diffs[argmin(len_diffs)]/lens[argmin(len_diffs)] < 0.2: #also wenn die passendste in länge nur 20% differt
            meditation_length = lens[argmin(len_diffs)]
        else:
            closest_meditations = get_two_closest(lens, meditation_length)
            resp = standard_response('Sorry, but I don\'t have a meditation of that length. Alternatively I can offer you one that is '+' or '.join([str(i) for i in closest_meditations])+' minutes long.')
            resp['payload']['google']['richResponse']['suggestions'] = [{'title': str(i)+' minutes'} for i in closest_meditations]
            resp['outputContexts'] = [{'name': req_json['session']+'/contexts/meditation-active', "lifespanCount": 5, 'parameters': {key: val for key, val in parameters.items() if key != 'meditation-length'}}]
            #TODO er vergisst den meditation-type for some fucking reason wieder. Rausfinden wie man das ändern kann v.v
            return resp

    correct_meditation = correct_type[str(round(meditation_length))]
    correct_meditation = json.loads(json.dumps(correct_meditation).replace('BASE_DIR', settings.MP3_ROOT_DOMAIN))
    resp_meditation['payload']['google']['richResponse']['items'][where_media]['mediaResponse']['mediaObjects'] = [correct_meditation]
    print("Selected Meditation", correct_meditation)
    #TODO: ein random bild bei den meditationen mitschicken
    # TODO vielleich nach beenden des mp3s fragen wie's war? https://developers.google.com/assistant/conversational/responses#MediaResponseHandlingCallback, https://stackoverflow.com/questions/53099327/autoplay-media-until-times-up-in-google-dialogflow
    return resp_meditation


def get_two_closest(lenlist, len):
    if len < lenlist[0]:
        return [lenlist[0]]
    elif len > lenlist[-1]:
        return [lenlist[-1]]
    for ind, elem in enumerate(lenlist):
        if len < elem:
            break
    return [lenlist[ind - 1], lenlist[ind]]

def get_username(json):
    for context in json['queryResult']['outputContexts']:
        if 'username' in context['parameters']:
            return context['parameters']['username']
    return None