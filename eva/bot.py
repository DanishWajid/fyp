# bot.py

import sys
sys.path.append("./")
import requests
from speech import Speech
import json
from math import floor
import traceback
from nlg import NLG
from knowledge import Knowledge
from copy import deepcopy

wit_ai_token = "Bearer FREE3BBMQ2OSQ7SOO2COJJV5ZRYDU2YQ"

normal_state = 0
add_user_state = 1
delete_user_state = 2
set_alarm_state = 3
check_news_state = 4
set_reminder_state = 5
to_do_list_state = 6
consult_encyclopedia_state = 7
set_note_state = 8
logout_state = 9
map_state = 10
set_todo_state = 11
currency_state = 12
idle_state = 100


class Bot(object):

    def __init__(self, user_obj):
        self.current_user = None
        self.nlg = NLG()
        self.speech = Speech()
        self.knowledge = Knowledge(user_obj)
        # self.update_current_user(user_obj, greet=False)  # __________________testing
        self.new_user = deepcopy(user_obj)
        self.tmp_time = None
        self.choice = None
        self.msg = None
        self.users = self.knowledge.update_users_list()
        self.state = normal_state
        self.speak = True

    # main loop
    def run(self):
        text = self.listen_loop()
        if text:
            self.generate_response(text)

    def listen_loop(self):
        recognizer, audio = self.speech.listen_for_audio()
        return self.speech.get_text(recognizer, audio)

    def check_user_logedin(self):
        return self.current_user is not None

    def logout_user(self, user_name):
        # logout the user
        pass

    def return_users(self):
        return self.users

    def update_current_user(self, user_obj, greet=True):
        self.current_user = user_obj
        self.knowledge.change_user(user_obj)
        if user_obj:
            self.nlg.change_user(user_obj.username)
            if greet:
                self.__text_action(self.nlg.greet())

    def generate_response(self, text=None):
        if text is not None:

            print(text)  # log
            if self.speak:
                requests.get("http://localhost:8080", {"text": text})  # send to our display

            try:
                r = requests.get(
                    'https://api.wit.ai/message?v=09/02/2018&q=%s'
                    % text, headers={"Authorization": wit_ai_token})

                print(r.text)  # remove later

                json_resp = json.loads(r.text)
                entities = None
                intent = None
                wiki = None

                if 'entities' in json_resp:
                    entities = json_resp['entities']

                if 'entities' in json_resp and \
                   'Intent' in json_resp['entities']:
                    intent = json_resp['entities']['Intent'][0]["value"]

                if 'entities' in json_resp and \
                   'wikipedia_search_query' in json_resp['entities']:
                    wiki = json_resp['entities']['wikipedia_search_query'][0]["value"]

                # check which in state eva is in

                if self.state == normal_state:

                    if intent == 'weather':
                        self.__weather_action(entities)
                    elif intent == 'news':
                        self.__news_action()
                    elif intent == 'maps':
                        self.state = float(map_state)
                    elif intent == 'joke':
                        self.__joke_action()
                    elif intent == 'alarm_set':
                        self.state = float(set_alarm_state)
                    elif intent == 'add_user':
                        self.state = float(add_user_state)
                    elif intent == 'del_user':
                        self.state = float(delete_user_state)
                    elif intent == 'set_todo' or ("add" in text and "task" in text):
                        self.state = float(set_todo_state)
                    elif intent == 'get_todo':
                        self.__get_todo()
                    elif intent == 'set_note':
                        self.state = float(set_note_state)
                    elif intent == 'set_reminder':
                        self.state = float(set_reminder_state)
                    elif intent == 'get_note':
                        self.__get_note()
                    elif intent == 'currency':
                        self.state = float(currency_state)
                    elif intent == 'logout':
                        self.state = float(logout_state)
                    elif wiki and "tell" in text and "about" in text:
                        self.__wiki_action(wiki)
                    else:  # No recognized intent
                        self.__text_action(
                            "I'm sorry, I don't know about that yet.")
                        return
                ###############################################################

                if floor(self.state) == float(logout_state):

                    if self.state == float(logout_state) + 0.0:
                        self.state = float(logout_state) + 0.1
                        self.__text_action(
                            "are you sure you want to logout?")
                        return

                    if self.state == float(logout_state) + 0.1:
                        if intent == 'yes':
                            self.state = normal_state
                            self.update_current_user(None)  # logout
                            self.__text_action("you have loged out")
                            return
                        elif intent == 'no':
                            self.state = normal_state
                            self.__text_action('okay')
                            return
                        else:
                            self.state = normal_state
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                ###############################################################

                if floor(self.state) == float(delete_user_state):

                    if self.state == float(delete_user_state) + 0.0:

                        if self.current_user._super == 'yes':
                            self.knowledge.update_users_list()

                            other_users = list(
                                filter(lambda x: x[0] is not
                                       self.current_user._id, self.users))

                            self.__text_action(
                                "which user you want to remove?")

                            if len(other_users):
                                self.state = float(delete_user_state) + 0.1

                                for i in range(len(other_users)):
                                    other_users[i] = str(
                                        i + 1) + " " + other_users[i][2]

                                self.__list_action(other_users)
                                return
                            else:
                                self.__text_action(
                                    "I'm sorry, there are no other users")
                                self.state = normal_state
                                return
                        else:
                            self.__text_action(
                                "I'm sorry, only super users can remove users")
                            self.state = normal_state
                            return

                    if self.state == float(delete_user_state) + 0.1:

                        self.choice = None

                        if 'entities' in json_resp and \
                           'number' in json_resp['entities']:
                            number = json_resp['entities']['number'][0]["value"]

                        other_users = list(
                            filter(lambda x: x[0] is not
                                   self.current_user._id, self.users))

                        self.choice = other_users[int(number) - 1][0]

                        if self.choice:
                            self.state = float(delete_user_state) + 0.2
                            self.__text_action(
                                "are you sure about '" +
                                other_users[int(number) - 1][2] + "'?")
                            return
                        else:
                            self.__text_action(
                                '''Please specify the user with number
                                   next to it''')

                            other_users = list(
                                filter(lambda x: x[0] is not
                                       self.current_user._id, self.users))

                            for i in range(len(other_users)):
                                other_users[i] = str(
                                    i + 1) + " " + other_users[i][2]

                            self.__list_action(other_users)
                            return

                    if self.state == float(delete_user_state) + 0.2:

                        if intent == 'yes':
                            self.knowledge.del_user(self.choice)
                            self.state = normal_state
                            self.__text_action("user removed")
                            return

                        elif intent == 'no':
                            self.state = float(delete_user_state) + 0.1
                            self.__text_action(
                                '''Please specify the user with number
                                   next to it''')

                            other_users = list(
                                filter(lambda x: x[0] is not
                                       self.current_user._id, self.users))

                            for i in range(len(other_users)):
                                other_users[i] = str(
                                    i + 1) + " " + other_users[i][2]

                            self.__list_action(other_users)
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                ###############################################################

                if floor(self.state) == float(set_note_state):

                    if self.state == float(set_note_state) + 0.0:

                        self.knowledge.update_users_list()

                        other_users = list(
                            filter(lambda x: x[0] is not self.current_user._id,
                                   self.users))

                        self.__text_action(
                            "For whom do you want to leave the note?")

                        if len(other_users):
                            self.state = float(set_note_state) + 0.1

                            for i in range(len(other_users)):
                                other_users[i] = str(
                                    i + 1) + " " + other_users[i][2]

                            self.__list_action(other_users)
                            return

                        else:
                            self.__text_action(
                                "I'm sorry, there are no other users")
                            self.state = normal_state
                            return

                    if self.state == float(set_note_state) + 0.1:

                        self.choice = None

                        if 'entities' in json_resp and \
                           'number' in json_resp['entities']:
                            number = json_resp['entities']['number'][0]["value"]

                        self.choice = self.users[number - 1][0]

                        if self.choice:
                            self.state = float(set_note_state) + 0.2
                            self.__text_action("what is your message?")
                            return
                        else:
                            self.__text_action(
                                "Please specify the user with number next to it")

                            other_users = list(
                                filter(lambda x: x[0] is not
                                       self.current_user._id, self.users))

                            for i in range(len(other_users)):
                                other_users[i] = str(
                                    i + 1) + " " + other_users[i][2]

                            self.__list_action(other_users)

                            return

                    if self.state == float(set_note_state) + 0.2:

                        self.msg = None

                        self.state = float(set_note_state) + 0.3
                        self.msg = text
                        self.__text_action(
                            "are you sure about '" + text + "'?")
                        return

                    if self.state == float(set_note_state) + 0.3:

                        if intent == 'yes':
                            self.knowledge.set_note(self.choice, self.msg)
                            self.state = normal_state
                            self.__text_action("Note sent to the user")
                            return

                        elif intent == 'no':
                            self.state = float(set_note_state) + 0.2
                            self.__text_action("what is your message?")
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                ###############################################################

                if floor(self.state) == float(set_reminder_state):

                    if self.state == float(set_reminder_state) + 0.0:

                        time_for_reminder = None

                        if 'entities' in json_resp and 'datetime' in json_resp['entities']:
                            time_for_reminder = json_resp['entities']['datetime'][0]["values"][0]["value"]

                        if time_for_reminder:
                            indx = time_for_reminder.find(":")
                            self.tmp_time = time_for_reminder[indx - 2:indx + 3]
                            self.state = float(set_reminder_state) + 0.1
                            self.__text_action(
                                "you sure you want to set a reminder for " + self.tmp_time + " ?")
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, Please tell the reminder time again")
                            self.state = normal_state
                            return

                    if self.state == float(set_reminder_state) + 0.1:
                        if intent == 'yes':
                            self.state = float(set_reminder_state) + 0.2
                            self.__text_action("what is the reminder?")
                            return
                        elif intent == 'no':
                            self.__text_action(
                                "Please tell correct reminder time")
                            self.state = normal_state
                            return
                        else:  # No recognized intent
                            self.state = normal_state
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                    if self.state == float(set_reminder_state) + 0.2:
                        self.msg = None
                        self.msg = text
                        self.__text_action(
                            "are you sure about '" + text + "'?")
                        self.state = float(set_reminder_state) + 0.3
                        return

                    if self.state == float(set_reminder_state) + 0.3:
                        if intent == 'yes':
                            self.knowledge.set_reminder(
                                self.msg, self.tmp_time)
                            self.state = normal_state
                            self.__text_action("reminder set up")
                            return
                        elif intent == 'no':
                            self.state = float(set_reminder_state) + 0.2
                            self.__text_action("what is your reminder?")
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                ###############################################################

                if floor(self.state) == float(set_alarm_state):

                    if self.state == float(set_alarm_state) + 0.0:

                        time_for_alarm = None

                        if 'entities' in json_resp and 'datetime' in json_resp['entities']:
                            time_for_alarm = json_resp['entities']['datetime'][0]["values"][0]["value"]

                        if time_for_alarm:
                            indx = time_for_alarm.find(":")
                            self.tmp_time = time_for_alarm[indx - 2:indx + 3]
                            self.state = float(set_alarm_state) + 0.1
                            self.__text_action(
                                "you sure you want to setup alarm for " + self.tmp_time + " ?")
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, Please tell the alarm time again")
                            self.state = normal_state
                            return

                    if self.state == float(set_alarm_state) + 0.1:

                        if intent == 'yes':
                            self.knowledge.set_alarm(self.tmp_time)
                            self.state = normal_state
                            self.__text_action("alarm set")
                            return
                        elif intent == 'no':
                            self.__text_action(
                                "Please tell correct alarm time")
                            self.state = normal_state
                            return
                        else:  # No recognized intent
                            self.state = normal_state
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                ###############################################################

                if floor(self.state) == float(add_user_state):

                    if self.state == float(add_user_state) + 0.0:
                        if self.current_user._super == 'yes':
                            self.state = float(add_user_state) + 0.1
                            self.__text_action(
                                "Please tell if the new user is a super user")
                            return
                        else:
                            self.__text_action(
                                "I'm sorry, only super users can add more users")
                            self.state = normal_state
                            return

                    if self.state == float(add_user_state) + 0.1:

                        if intent == 'yes':
                            self.new_user._super == 'yes'
                            self.state = float(add_user_state) + 0.2
                            self.__text_action(
                                "what is new users 'username' ?")
                            return
                        elif intent == 'no':
                            self.state = float(add_user_state) + 0.2
                            self.__text_action(
                                "what is new users 'username' ?")
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                    if self.state == float(add_user_state) + 0.2:

                        if text:
                            self.new_user.username == text
                            self.state = float(add_user_state) + 0.3
                            self.__text_action(
                                "are you sure about '" + text + "'?")
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                    if self.state == float(add_user_state) + 0.3:

                        if intent == 'yes':
                            self.state = float(add_user_state) + 0.4
                            self.__text_action(
                                "what is new users 'password' ?")
                            return
                        elif intent == 'no':
                            self.state = float(add_user_state) + 0.3
                            self.__text_action(
                                "what is new users 'username' ?")
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.\n Are you sure about '" + self.new_user.username + "'?")
                            return

                    if self.state == float(add_user_state) + 0.4:

                        if text:
                            self.new_user.password == text
                            self.state = float(add_user_state) + 0.5
                            self.__text_action(
                                "are you sure about '" + text + "'?")
                            return
                        else:
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                    if self.state == float(add_user_state) + 0.5:

                        if intent == 'yes':
                            self.state = normal_state
                            self.__text_action("new user added")
                            self.knowledge.add_user(self.new_user)
                            return
                        elif intent == 'no':
                            self.state = float(add_user_state) + 0.4
                            self.__text_action(
                                "what is new users 'password' ?")
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.\n Are you sure about '" + self.new_user.password + "'?")
                            return

                ###############################################################

                if floor(self.state) == float(map_state):

                    if self.state == float(map_state) + 0.0:
                        location = None
                        if entities is not None:
                            if 'location' in entities:
                                location = entities['location'][0]["value"]
                            if "wikipedia_search_query" in entities:
                                location = entities['wikipedia_search_query'][0]["value"]

                        if location is not None:
                            self.state = float(map_state) + 0.1
                            self.speak = False
                            maps_url = self.knowledge.get_map_url(location)
                            maps_action = "Sure. Here's a map of %s." % location
                            body = {'url': maps_url}
                            print(body)
                            requests.get("http://localhost:8080", {"image": (maps_url)})
                            self.speech.synthesize_text(maps_action)
                            return
                        else:
                            self.state = normal_state
                            self.__text_action(
                                "I'm sorry, I couldn't understand what location you wanted.")
                            return

                    if self.state == float(map_state) + 0.1:

                        if intent == 'done':
                            self.speak = True
                            self.state = normal_state
                            done = self.nlg.done()
                            self.__text_action(done)
                            return

                ###############################################################

                if floor(self.state) == float(set_todo_state):

                    if self.state == float(set_todo_state) + 0.0:

                        self.state = float(set_todo_state) + 0.1
                        self.__text_action("what is your task?")
                        return

                    if self.state == float(set_todo_state) + 0.1:

                        self.msg = text
                        self.state = float(set_todo_state) + 0.2
                        self.__text_action(
                            "are you sure about '" + text + "'?")
                        return

                    if self.state == float(set_todo_state) + 0.2:

                        if intent == 'yes':
                            self.knowledge.set_todo(self.msg)
                            self.state = normal_state
                            self.__text_action("todo set!")
                            return
                        elif intent == 'no':
                            self.state = float(set_todo_state) + 0.1
                            self.__text_action("what is your task?")
                            return
                        else:  # No recognized intent
                            self.__text_action(
                                "I'm sorry, I don't know about that yet.")
                            return

                ###############################################################

                # if floor(self.state) == float(idle_state):
                #
                #     if self.state == float(idle_state) + 0.0:
                #
                #         if "hey" in text and "there" in text:
                #             self.state = float(idle_state) + 0.1
                #             self.speak = False
                #             maps_url = self.knowledge.get_map_url(location)
                #             maps_action = "Sure. Here's a map of %s." % location
                #             body = {'url': maps_url}
                #             print(body)
                #             requests.get("http://localhost:8080", {"image": (maps_url)})
                #             self.speech.synthesize_text(maps_action)
                #             return
                #         else:
                #             self.state = normal_state
                #             self.__text_action(
                #                 "I'm sorry, I couldn't understand what location you wanted.")
                #             return
                #
                #     if self.state == float(idle_state) + 0.1:
                #
                #         if intent == 'done':
                #             self.speak = True
                #             self.state = normal_state
                #             done = self.nlg.done()
                #             self.__text_action(done)
                #             return

                ###############################################################

                if floor(self.state) == float(currency_state):

                    if self.state == float(currency_state) + 0.0:

                        currency = self.knowledge.find_currency()

                        if currency:
                            requests.get("http://localhost:8080",
                                         {"currency": ','.join(str(v) for v in currency)})
                            self.state = float(currency_state) + 0.1
                            self.speak = False
                            return
                        else:
                            self.__text_action(
                                        "I had some trouble finding currency rates for you")
                            self.state = normal_state
                            return

                    if self.state == float(currency_state) + 0.1:

                        if intent == 'done':
                            self.speak = True
                            self.state = normal_state
                            done = self.nlg.done()
                            self.__text_action(done)
                            return

                ###############################################################

            except Exception as e:
                print("Failed wit!")
                print(e)
                traceback.print_exc()
                self.__text_action(
                    "I'm sorry, I couldn't understand what you meant by that")
                return

    def __joke_action(self):
        joke = self.nlg.joke()
        self.__text_action(joke)

    def __news_action(self):

        headlines = self.knowledge.get_news()

        if headlines:
            self.__list_action(headlines)
        else:
            self.__text_action("I had some trouble finding news for you")

    def __wiki_action(self, q):

        summary = self.knowledge.get_wiki(q)

        if summary:
            self.__text_action(summary)
        else:
            self.__text_action("I had some trouble finding about " + q)

    def __weather_action(self, nlu_entities=None):

        weather_obj = self.knowledge.find_weather()
        weather_speech = self.nlg.weather(weather_obj)

        self.__list_action(weather_speech)

    def __maps_action(self, entities):

        location = None

        if entities is not None:
            if 'location' in entities:
                location = entities['location'][0]["value"]
            if "wikipedia_search_query" in entities:
                location = entities['wikipedia_search_query'][0]["value"]

        if location is not None:
            maps_url = self.knowledge.get_map_url(location)
            maps_action = "Sure. Here's a map of %s." % location
            body = {'url': maps_url}
            # requests.post("http://localhost:8080/image", data=json.dumps(body))
            print(body)
            requests.get("http://localhost:8080", {"image": (maps_url)})
            self.speech.synthesize_text(maps_action)
        else:
            self.__text_action(
                "I'm sorry, I couldn't understand what location you wanted.")

    def __get_todo(self):
        todo = self.knowledge.get_todo()
        self.__text_action("The following is your todo list")
        self.__list_action(todo, speak=False)

    def __get_note(self):
        notes = self.knowledge.get_note()
        self.__text_action("You have the following messages")
        self.__list_action(notes, speak=False)

    def text_action(self, text=None):
        self.__text_action(text)

    def __text_action(self, text=None):
        if text is not None:
            requests.get("http://localhost:8080", {"text": text})
            self.speech.synthesize_text(text)

    def __list_action(self, listin=None, speak=True):
        if listin is not None:
            requests.get("http://localhost:8080", {"list": "_".join(listin)})
            if speak:
                for sentns in listin:
                    self.speech.synthesize_text(sentns)
