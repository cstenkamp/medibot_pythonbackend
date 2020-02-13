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

