
import requests

apiurl = "https://mshahzaib.pythonanywhere.com"

_id = 2
choice = 4
msg = "asdf"

r = requests.get(apiurl + "/note/add/"+"sender"+"&"+msg+"&"+"this time"+"&"+str(choice))