import json
from os import path
from copy import deepcopy

from sample_jsons import SAMPLE_PAYLOAD_JSON, SAMPLE_RESPONSE_JSON, SAMPLE_IMAGE_JSON
from sentiment import create_sentiment_graph
import userdb
import settings

MEDITATION_STANDARD_LENGTH = 3

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
    elif intent_name == 'sentiment.analyse':
        return show_sentiment(req_json)


def show_sentiment(req_json):
    username = userdb.UserSession.query.filter(userdb.UserSession.sessionid == req_json['session']).one_or_none().user
    imgpath = create_sentiment_graph(username, show_initial=2, show_starplot=True) #TODO show_initial kann 3 verschiedene Werte haben und show_starplot auch 2!
    imgpath = imgpath.replace(settings.EMOTION_BASE_DIR, settings.IMAGE_DOMAIN)
    resp = SAMPLE_IMAGE_JSON
    resp['payload']['google']['richResponse']['items'][1]['basicCard']['image']['url'] = imgpath
    return resp



def standard_response(text):
    resp = deepcopy(SAMPLE_RESPONSE_JSON)
    resp['payload']['google']['richResponse']['items'][0]['simpleResponse']['textToSpeech'] = text
    return resp



def store_sentiment(req_json):
    assert req_json['queryResult']['allRequiredParamsPresent']
    print("storing sentiment")
    #username = req_json['queryResult']['parameters']['username'].lower() #TODO warum ist er einfach gone?!
    username = userdb.UserSession.query.filter(userdb.UserSession.sessionid == req_json['session']).one_or_none().user

    if req_json['queryResult']['intent']['displayName'] == 'sentiment.eval.initial':
        strength = req_json['queryResult']['parameters']['initial-sentiment-strength']
        sentiment = req_json['queryResult']['parameters']['initial-sentiment']
        userdb.store_sentiment(username, sentiment, strength, is_intitial=True)
    else:
        strength = req_json['queryResult']['parameters']['final-sentiment-strength']
        sentiment = req_json['queryResult']['parameters']['final-sentiment']
        userdb.store_sentiment(username, sentiment, strength, is_initial=False)

    return standard_response("Okay, I noted down that feeling.")




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
    assert req_json['queryResult']['allRequiredParamsPresent']
    assert get_username(req_json) # TODO ne andere response zurückgeben falls kein User

    print('starting meditation...')
    meditation_type = req_json['queryResult']['parameters']['meditation-type']
    meditation_length = req_json['queryResult']['parameters']['meditation-length']
    meditation_length = int(meditation_length) if meditation_length else MEDITATION_STANDARD_LENGTH
    #TODO: wenn json['queryResult']['parameters']['meditation-length'] gesetzt ist erst in x minuten

    resp_meditation = SAMPLE_PAYLOAD_JSON
    where_media = [num for num, i in enumerate(resp_meditation['payload']['google']['richResponse']['items']) if 'mediaResponse' in i.keys()][0]

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
            #resp['outputContexts'] = [{'name': req_json['session']+'/contexts/meditation-active', "lifespanCount": 5, 'parameters': {key: val for key, val in req_json['queryResult']['parameters'].items() if key != 'meditation-length'}}]
            resp['outputContexts'] = [{key: (val if key != 'parameters' else {k2: v2 for k2,v2 in val.items() if k2 != 'meditation-length'}) for key, val in i.items()} for i in req_json['queryResult']['outputContexts']]
            #TODO er vergisst den meditation-type for some fucking reason wieder. Rausfinden wie man das ändern kann v.v
            print("returning", resp)
            return resp


    correct_meditation = correct_type[str(meditation_length)]
    correct_meditation = json.loads(json.dumps(correct_meditation).replace('BASE_DIR', settings.MP3_ROOT_DOMAIN))
    resp_meditation['payload']['google']['richResponse']['items'][where_media]['mediaResponse']['mediaObjects'] = [correct_meditation]
    print("Selected Meditation", correct_meditation)
    #TODO: ein random bild bei den meditationen mitschicken

    # TODO vielleich nach beenden des mp3s fragen wie's war? https://developers.google.com/assistant/conversational/responses#MediaResponseHandlingCallback, https://stackoverflow.com/questions/53099327/autoplay-media-until-times-up-in-google-dialogflow
    #https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2#webhookresponse
    # a = json.loads("""{
    #     "fulfillmentText": "<speak>This is a text response<break time="3s"/>asdf</speak>"
    #      }""")

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