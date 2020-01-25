import json


MEDITATION_STANDARD_LENGTH = 3

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

    if meditation_length == 3:
        file = 'res/FreeMindfulness3MinuteBreathing.mp3'

        #https://cloud.google.com/dialogflow/docs/reference/rpc/google.cloud.dialogflow.v2#webhookresponse
        # tmp = """{
        #     "fulfillmentText": "<speak>This is a text response<break time="3s"/>asdf</speak>"
        #      }"""
        # a = json.loads(tmp)
        #a = {'fulfillmentText': '<speak>This is a text response<break time="3s"/>asdf</speak>'}
        # a = {'conversationToken': '["_actions_on_google"]',
        #      'expectedInputs': [
        #          {'inputPrompt': {
        #              'richInitialPrompt': {
        #                  'items': [
        #                      {
        #                          'simpleResponse': {
        #                              'textToSpeech': 'My favarata albam'
        #                          },
        #                      },
        #                      {
        #                         'mediaResponse'
        #                      }
        #                  ]
        #              }
        #          }}
        #      ]}

        a = json.loads("""{
  "payload": {
    "google": {
      "expectUserResponse": true,
      "richResponse": {
        "items": [
          {
            "simpleResponse": {
              "textToSpeech": "This is a media response example."
            }
          },
          {
            "mediaResponse": {
              "mediaType": "AUDIO",
              "mediaObjects": [
                {
                  "contentUrl": "https://cstenkamp.de/FreeMindfulness3MinuteBreathing.mp3",
                  "description": "A funky Jazz tune",
                  "icon": {
                    "url": "https://storage.googleapis.com/automotive-media/album_art.jpg",
                    "accessibilityText": "Album cover of an ocean view"
                  },
                  "name": "Jazz in Paris"
                }
              ]
            }
          }
        ],
        "suggestions": [
          {
            "title": "Basic Card"
          },
          {
            "title": "List"
          },
          {
            "title": "Carousel"
          },
          {
            "title": "Browsing Carousel"
          }
        ]
      }
    }
  }
}
""")

        return a


def get_username(json):
    for context in json['queryResult']['outputContexts']:
        if 'username' in context['parameters']:
            return context['parameters']['username']
    return None