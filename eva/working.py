from wikiapi import WikiApi
import requests
import json
wiki = WikiApi()


wit_ai_token = "Bearer FREE3BBMQ2OSQ7SOO2COJJV5ZRYDU2YQ"
r = requests.get('https://api.wit.ai/message?v=09/02/2018&q=%s' % "tell me about pakistan",
                                 headers={"Authorization": wit_ai_token})

print (r.text)

json_resp = json.loads(r.text)

print (json_resp['entities']['wikipedia_search_query'][0]["value"])