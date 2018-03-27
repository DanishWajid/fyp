import requests
import json
import feedparser
import datetime


class Knowledge(object):
    def __init__(self, _current_user):
        self.current_user = _current_user
        self.apiurl = "https://mshahzaib.pythonanywhere.com"


    def find_weather(self):

        lat = 33.684420
        lon = 73.047885

        weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s" % ("dafddca65618d5947f1a23f2f3f51ecf", lat, lon)
        r = requests.get(weather_req_url)
        weather_json = json.loads(r.text)

        temperature = int(weather_json['currently']['temperature'])

        current_forecast = weather_json['currently']['summary']
        wind_speed = int(weather_json['currently']['windSpeed'])

        return {'temperature': temperature, 'windSpeed': wind_speed, 'current_forecast': current_forecast}

    def get_news(self):
        
        url = ('https://newsapi.org/v2/top-headlines?'
        'country=us&'
        'category=technology&'
        'apiKey=ff33f4d1d2c1455eafcb410bef3a2375')

        response = requests.get(url)
        news_dict = json.loads(response.content)["articles"]
        headlines = []
        count  = 0
        for newz in news_dict:
            headlines.append(newz["title"])
            count += 1
            if count == 5:
                break

        return headlines

        # return ret_headlines

    def todo(self):
        print("getting todo:",self.apiurl + "/todo/get")
        r = requests.get(self.apiurl + "/todo/get")
        resp = json.loads(r.text)
        toReturn = []
        for note in resp["todos"]:
            toReturn.append(note[1])
        return toReturn

    def note(self):
        print("getting note:",self.apiurl + "/note/get")
        r = requests.get(self.apiurl + "/note/get")
        resp = json.loads(r.text)
        toReturn = []
        for note in resp["notes"]:
            toReturn.append(note[3])
        return toReturn


    def add_user(self, user_obj):
        print("adding user")
        r = requests.get(self.apiurl + "/user/add/"+user_obj._super+"&face&"+user_obj.username+"&"+user_obj.username+"&"+user_obj.password)

    def set_alarm(self, alarmtime):
        print("setting alarm")
        r = requests.get(self.apiurl + "/alarm/add/"+alarmtime+"&"+str(self.current_user._id))

    def update_users_list(self):
        print("checking user")
        r = requests.get(self.apiurl + "/user/get")
        resp = json.loads(r.text)
        toReturn = []

        for u in resp['users']:
            toReturn.append(u)

        return toReturn


