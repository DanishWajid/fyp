import requests, json


# wit_ai_token = "Bearer FREE3BBMQ2OSQ7SOO2COJJV5ZRYDU2YQ"
# r = requests.get('https://api.wit.ai/message?v=09/02/2018&q=%s' % "show my messages",
#                                  headers={"Authorization": wit_ai_token})

# print (r.text)############################ remove later

# json_resp = json.loads(r.text)

# print (json_resp)

apiurl = "https://mshahzaib.pythonanywhere.com"
r = requests.get(apiurl + "/user/get")
resp = json.loads(r.text)
toReturn = []

for u in resp['users']:
    toReturn.append(u)

print (toReturn)