import json
from os import path

from sample_jsons import SAMPLE_PAYLOAD_JSON


MEDITATION_STANDARD_LENGTH = 3

MP3_ROOT_DIR = 'https://cstenkamp.de/meditation_files'
FILES_ROOT_DIR = '/var/www/medibot_pythonbackend'


def handle_intent(intent_name, req_json):
    if intent_name == 'meditation.start':
        return start_meditation(req_json)


def start_meditation(req_json):
    assert req_json['queryResult']['allRequiredParamsPresent']
    assert get_username(req_json) # TODO ne andere response zurückgeben falls kein User

    print('starting meditation...')
    meditation_length = req_json['queryResult']['parameters']['meditation-length']
    meditation_length = int(meditation_length) if meditation_length else MEDITATION_STANDARD_LENGTH
    #TODO: wenn json['queryResult']['parameters']['meditation-length'] gesetzt ist erst in x minuten

    resp_meditation = SAMPLE_PAYLOAD_JSON
    where_media = [num for num, i in enumerate(resp_meditation['payload']['google']['richResponse']['items']) if 'mediaResponse' in i.keys()][0]

    with open(path.join(FILES_ROOT_DIR, 'meditations.json')) as json_file:
        meditation_data = json.load(json_file)

    if str(meditation_length) in list(meditation_data.keys()):
        correct_meditation = meditation_data[str(meditation_length)]
        correct_meditation = json.loads(json.dumps(correct_meditation).replace('BASE_DIR', MP3_ROOT_DIR))
        resp_meditation['payload']['google']['richResponse']['items'][where_media]['mediaResponse']['mediaObjects'] = [correct_meditation]
        #TODO: ein random bild bei den meditationen mitschicken

        #https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2#webhookresponse
        # a = json.loads("""{
        #     "fulfillmentText": "<speak>This is a text response<break time="3s"/>asdf</speak>"
        #      }""")

        return resp_meditation
    return ''


def get_username(json):
    for context in json['queryResult']['outputContexts']:
        if 'username' in context['parameters']:
            return context['parameters']['username']
    return None