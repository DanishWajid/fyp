import requests
import json
from datetime import datetime
from wikiapi import WikiApi


class Knowledge(object):

    def __init__(self, _current_user):
        self.current_user = _current_user
        self.apiurl = "https://mshahzaib.pythonanywhere.com"

    def change_user(self, curr_user):
        self.current_user = curr_user

    def find_weather(self):

        lat = 33.684420
        lon = 73.047885

        weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s" % (
            "dafddca65618d5947f1a23f2f3f51ecf", lat, lon)
        r = requests.get(weather_req_url)
        weather_json = json.loads(r.text)

        temperature = int(weather_json['currently']['temperature'])

        current_forecast = weather_json['currently']['summary']
        wind_speed = int(weather_json['currently']['windSpeed'])

        return {'temperature': temperature, 'windSpeed': wind_speed,
                'current_forecast': current_forecast}

    def get_news(self):

        url = ('https://newsapi.org/v2/top-headlines?'
               'country=us&'
               'category=technology&'
               'apiKey=ff33f4d1d2c1455eafcb410bef3a2375')

        response = requests.get(url)
        news_dict = json.loads(response.content)["articles"]
        headlines = []
        count = 0
        for newz in news_dict:
            headlines.append(newz["title"])
            count += 1
            if count == 5:
                break

        return headlines

    def get_wiki(self, query):
        wiki = WikiApi()
        toReturn = wiki.get_article(wiki.find(query)[0]).summary
        if len(toReturn) > 220:
            toReturn = toReturn[:toReturn.find(".", 220)]
        return toReturn

    def get_todo(self):
        print("getting todo:", self.apiurl + "/todo/get")
        r = requests.get(self.apiurl + "/todo/get")
        resp = json.loads(r.text)
        toReturn = []
        for note in resp["todos"]:
            toReturn.append(note[1])
        return toReturn

    def set_todo(self, todo, user_id):
        print("adding todo")
        requests.get(self.apiurl + "/todo/add/" + todo + "&" + user_id)

    def get_note(self):
        print("getting note")
        r = requests.get(self.apiurl + "/note/get")
        resp = json.loads(r.text)
        toReturn = []
        for note in resp["notes"]:
            toReturn.append(note[2] + "<br>" + note[1] +
                            "<span style='float:right';>" + note[3] + "</span>")
        return toReturn

    def set_note(self, choice, msg):
        print("setting note")
        requests.get(self.apiurl + "/note/add/" + self.current_user.username +
                     "&" + msg + "&" +
                     datetime.now().strftime("%I:%M%p - %d %b %y") + "&" +
                     str(choice))

    def set_user(self, user_obj):
        print("adding user")
        requests.get(self.apiurl + "/user/add/" + user_obj._super +
                     "&" + user_obj.username + "&" + user_obj.password)

    def del_user(self, usr_id):
        print("removing user")
        requests.get(self.apiurl + "/user/del/" + str(usr_id))

    def set_alarm(self, alarmtime):
        print("setting alarm")
        requests.get(self.apiurl + "/alarm/add/" +
                     alarmtime + "&" + str(self.current_user._id))

    def set_reminder(self, reminder, r_time):
        print("setting reminder")
        requests.get(self.apiurl + "/reminder/add/" +
                     r_time + "&" + reminder + "&" +
                     str(self.current_user._id))

    def update_users_list(self):
        print("checking user")
        r = requests.get(self.apiurl + "/user/get")
        resp = json.loads(r.text)
        toReturn = []

        for u in resp['users']:
            toReturn.append(u)

        return toReturn

    def find_currency(self):
        # pkr is the base currency you want to use
        url = '''https://v3.exchangerate-api.com/bulk/
               fe12dc4317270c8c24e99e6a/PKR'''

        # Making our request
        response = requests.get(url)
        curr_json = json.loads(response.text)
        currency = []

        currency.append(1 / curr_json['rates']['USD'])
        currency.append(1 / curr_json['rates']['EUR'])
        currency.append(1 / curr_json['rates']['GBP'])
        currency.append(1 / curr_json['rates']['SAR'])
        currency.append(1 / curr_json['rates']['CAD'])
        currency.append(1 / curr_json['rates']['AUD'])

        return currency

    def get_map_url(self, location):
        return '''http://maps.googleapis.com/maps/api/staticmap?
                  center=%s&zoom=15&scale=true&size=1200x600&
                  maptype=roadmap&format=png''' % location
