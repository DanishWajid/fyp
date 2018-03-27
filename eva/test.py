from wit import Wit


wit_ai_token = "FREE3BBMQ2OSQ7SOO2COJJV5ZRYDU2YQ"

client = Wit(wit_ai_token)
print (client.message('set an alarm tomorrow at 7am'))