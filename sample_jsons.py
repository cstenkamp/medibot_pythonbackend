SAMPLE_PAYLOAD_JSON = {
    "payload": {
        "google": {
            "expectUserResponse": True,
            "richResponse": {
                "items": [
                    {
                        "simpleResponse": {
                            "textToSpeech": "Ok, here is a meditation for you."
                        }
                    },
                    {
                        "mediaResponse": {
                            "mediaType": "AUDIO",
                            "mediaObjects": [
                                {
                                    "name": "3 Minute Meditation",
                                    "contentUrl": "http://www.freemindfulness.org/FreeMindfulness3MinuteBreathing.mp3",
                                    "description": "3 Minute Meditation",
                                    "largeImage": {
                                        "url": "https://storage.googleapis.com/automotive-media/album_art.jpg",
                                        "accessibilityText": "Album cover of an ocean view"
                                    }
                                }
                            ]
                        }
                    }
                ],
                "suggestions": [
                    {
                        "title": "That was appropriate"
                    },
                    {
                        "title": "I didn't like this one"
                    },
                ]
            }
        }
    }
}

SAMPLE_RESPONSE_JSON = {
    "payload": {
        "google": {
            "expectUserResponse": True,
            "richResponse": {
                "items": [
                    {
                        "simpleResponse": {
                            "textToSpeech": "Ok, here is a meditation for you."
                        }
                    }
                ],
                "suggestions": []
            }
        }
    }
}


SAMPLE_IMAGE_JSON = {
  "payload": {
    "google": {
      "expectUserResponse": True,
      "richResponse": {
        "items": [
          {
            "simpleResponse": {
              "textToSpeech": "Here's your emotional history"
            }
          },
          {
            "basicCard": {
              "title": "Your emotional history with me",
              "image": {
                "url": "IMAGE_URL",
                "accessibilityText": "<bargraph with your emotional history>"
              },
              "imageDisplayOptions": "DEFAULT"
            }
          }
        ]
      }
    }
  }
}


SAMPLE_LIST_JSON = {
  "payload": {
    "google": {
      "expectUserResponse": True,
      "systemIntent": {
        "intent": "actions.intent.OPTION",
        "data": {
          "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
          "listSelect": {
            "title": "Common Questions",
            "items": []
          }
        }
      },
      "richResponse": {
        "items": [
          {
            "simpleResponse": {
              "textToSpeech": "This is a list example."
            }
          }
        ]
      }
    }
  }
}

SAMPLE_LISTITEM_JSON =  {
    "optionInfo": {
      "key": "SELECTION_KEY_ONE",
      "synonyms": [
        "synonym 1",
        "synonym 2",
        "synonym 3"
      ]
    },
    "description": "This is a description of a list item.",
    "image": {
      "url": "https://storage.googleapis.com/actionsresources/logo_assistant_2x_64dp.png",
      "accessibilityText": "Image alternate text"
    },
    "title": "Title of First List Item"
  }

SAMPLE_LISTITEM_JSON_SHORT =  {
    "optionInfo": {
      "key": "SELECTION_KEY_ONE",
      "synonyms": []
    },
    "title": "Title of First List Item"
  }