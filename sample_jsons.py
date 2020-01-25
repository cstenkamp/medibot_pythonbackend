SAMPLE_PAYLOAD_JSON = {
    "payload": {
        "google": {
            "expectUserResponse": False,
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