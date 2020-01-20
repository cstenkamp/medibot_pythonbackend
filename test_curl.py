import requests
import json
import os
from os.path import join

import curlify

URL = 'https://www.cstenkamp.de/medibot/'

content = json.dumps('''{
	"responseId": "ea3d77e8-ae27-41a4-9e1d-174bd461b68c",
	"session": "projects/your-agents-project-id/agent/sessions/88d13aa8-2999-4f71-b233-39cbf3a824a0",
	"queryResult": {
		"queryText": "user's original query to your agent",
		"parameters": {
			"param": "param value"
		},
		"allRequiredParamsPresent": true,
		"fulfillmentText": "Text defined in Dialogflow's console for the intent that was matched",
		"fulfillmentMessages": [
			{
				"text": {
					"text": [
						"Text defined in Dialogflow's console for the intent that was matched"
					]
				}
			}
		],
		"outputContexts": [
			{
				"name": "projects/your-agents-project-id/agent/sessions/88d13aa8-2999-4f71-b233-39cbf3a824a0/contexts/generic",
				"lifespanCount": 5,
				"parameters": {
					"param": "param value"
				}
			}
		],
		"intent": {
			"name": "projects/your-agents-project-id/agent/intents/29bcd7f8-f717-4261-a8fd-2d3e451b8af8",
			"displayName": "Matched Intent Name"
		},
		"intentDetectionConfidence": 1,
		"diagnosticInfo": {},
		"languageCode": "en"
	},
	"originalDetectIntentRequest": {}
}''')

print(content)

requestHeaders = {
	"Content-Type": "application/json",
    # "X-Api-Key": API_KEY,
}


def post_command():
	reqres = requests.post(URL, headers=requestHeaders, data=content)
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


def main():
	res = post_command()
	print('\n'.join(res))


if __name__ == '__main__':
	main()


