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


wit_ai_token = "Bearer FREE3BBMQ2OSQ7SOO2COJJV5ZRYDU2YQ"
#_id,_super,_face,name,username,password

current_user = None
all_users = []

normal_state = 0

face_detection_state = 1
login_state = 2
add_user_state = 3
delete_user_state = 4
set_alarm_state = 5
check_news_state = 6
listen_joke_state = 7
weather_updates_state = 8
check_currency_state = 9
watch_video_state = 10
leave_a_note_state = 11
display_maps_state = 12
set_reminder_state = 13
to_do_list_state = 14
consult_encyclopedia_state = 15
logout_state = 16

class Bot(object):

    def __init__(self, user_obj):
        self.current_user = None
        self.nlg = NLG()
        self.speech = Speech()
        self.knowledge = Knowledge(user_obj)
            
        # self.update_current_user(user_obj) #____________________________________________________testing
        self.new_user = user_obj
        self.alarm = None
        self.users = self.knowledge.update_users_list()
        self.state = float(normal_state)
        self.start_time = float(normal_state)
        
        
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

    def update_current_user(self, user_obj):
        self.current_user = user_obj
        self.nlg.change_user(user_obj.username)
        self.__text_action(self.nlg.greet())


    def generate_response(self, text=None):
        if text is not None:

            print(text) # log

            # send to our display
            requests.get("http://localhost:8080", {"text": text} )

            # get intents
            try:
                r = requests.get('https://api.wit.ai/message?v=09/02/2018&q=%s' % text,
                                 headers={"Authorization": wit_ai_token})

                print (r.text)############################ remove later
                
                json_resp = json.loads(r.text)
                entities = None
                intent = None

                if 'entities' in json_resp :
                    entities = json_resp['entities']
                    

                if 'entities' in json_resp and 'Intent' in json_resp['entities']:
                    intent = json_resp['entities']['Intent'][0]["value"]
                

                # check which in state eva is in

                if self.state == normal_state: 

                    if intent == 'greeting':
                        self.__text_action(self.nlg.greet())
                    elif intent == 'weather':
                        self.__weather_action(entities)
                    elif intent == 'news':
                        self.__news_action()
                    elif intent == 'maps':      
                        self.__maps_action(entities)
                    elif intent == 'add_user':
                        self.state = float(add_user_state)
                    elif intent == 'alarm_set':
                        self.state = float(set_alarm_state)
                    elif intent == 'joke':
                        self.__joke_action()
                    elif intent == 'get_todo':
                        self.__todo()
                    elif intent == 'get_note':
                        self.__note()
                    elif intent == 'currency':
                        self.__currency()
                    elif 'entities' in json_resp and 'wikipedia_search_query' in json_resp['entities']:
                        self.__wiki_action(json_resp['entities']['wikipedia_search_query'][0]["value"])
                    else: # No recognized intent
                        self.__text_action("I'm sorry, I don't know about that yet.")
                        return

                ######################                      ######################                      ######################


                # if floor(self.state) == float(consult_encyclopedia_state):

                #     if self.state == float(consult_encyclopedia_state) + 0.0:

                #         time_for_alarm = None

                #         if 'entities' in json_resp and 'datetime' in json_resp['entities']:
                #             time_for_alarm = json_resp['entities']['datetime'][0]["values"][0]["value"]

                #         if time_for_alarm:
                #             self.alarm = time_for_alarm[11:17]
                #             self.state = float(set_alarm_state) + 0.1
                #             self.__text_action("you sure you want to setup alarm for " + time_for_alarm[11:17] + " ?")
                #             return
                #         else: # No recognized intent
                #             self.__text_action("I'm sorry, Please tell the alarm time again")
                #             self.state = normal_state
                #             return

                #     if self.state == float(consult_encyclopedia_state) + 0.1:

                #         if intent == 'yes':
                #             self.knowledge.set_alarm(self.alarm)
                #             self.state = normal_state
                #             self.__text_action("alarm set")
                #             return
                #         elif intent == 'no':
                #             self.__text_action("Please tell correct alarm time")
                #             self.state = normal_state
                #             return
                #         else: # No recognized intent
                #             self.state = normal_state
                #             self.__text_action("I'm sorry, I don't know about that yet.")
                #             return
                
                #############################################################################################################

                if floor(self.state) == float(set_alarm_state):

                    if self.state == float(set_alarm_state) + 0.0:

                        time_for_alarm = None

                        if 'entities' in json_resp and 'datetime' in json_resp['entities']:
                            time_for_alarm = json_resp['entities']['datetime'][0]["values"][0]["value"]

                        if time_for_alarm:
                            self.alarm = time_for_alarm[11:17]
                            self.state = float(set_alarm_state) + 0.1
                            self.__text_action("you sure you want to setup alarm for " + time_for_alarm[11:17] + " ?")
                            return
                        else: # No recognized intent
                            self.__text_action("I'm sorry, Please tell the alarm time again")
                            self.state = normal_state
                            return

                    if self.state == float(set_alarm_state) + 0.1:

                        if intent == 'yes':
                            self.knowledge.set_alarm(self.alarm)
                            self.state = normal_state
                            self.__text_action("alarm set")
                            return
                        elif intent == 'no':
                            self.__text_action("Please tell correct alarm time")
                            self.state = normal_state
                            return
                        else: # No recognized intent
                            self.state = normal_state
                            self.__text_action("I'm sorry, I don't know about that yet.")
                            return
                
                #############################################################################################################


                if floor(self.state) == float(add_user_state):
            
                    if self.state == float(add_user_state) + 0.0:
                        if current_user._super == 'yes':
                            self.state = float(add_user_state) + 0.1
                            self.new_user = user(_id_arg=0, _super_arg="yes", username_arg="Danish", password_arg="pass123")
                            self.__text_action("Please tell if the new user is a super user")
                            return
                        else:
                            self.__text_action("I'm sorry, only super users can add more users")
                            self.state = normal_state
                            return

                    if self.state == float(add_user_state) + 0.1:

                        if intent == 'yes':
                            self.new_user._super == 'yes'
                            self.state = float(add_user_state) + 0.2
                            self.__text_action("what is new users 'username' ?")
                            return
                        elif intent == 'no':
                            self.state = float(add_user_state) + 0.2
                            self.__text_action("what is new users 'username' ?")
                            return
                        else: # No recognized intent
                            self.__text_action("I'm sorry, I don't know about that yet.")
                            return

                    if self.state == float(add_user_state) + 0.2:
                        name = None

                        if 'entities' in json_resp and 'contact' in json_resp['entities']:
                            name = json_resp['entities']['contact'][0]["value"]

                        if name:
                            self.new_user.username == name
                            self.state = float(add_user_state) + 0.3
                            self.__text_action("are you sure about '"+name+"'?")
                            return
                        else: # No recognized intent
                            self.__text_action("I'm sorry, I don't know about that yet.")
                            return

                    if self.state == float(add_user_state) + 0.3:

                        if intent == 'yes':
                            self.state = float(add_user_state) + 0.4
                            self.__text_action("what is new users 'password' ?")
                            return
                        elif intent == 'no':
                            self.state = float(add_user_state) + 0.3
                            self.__text_action("what is new users 'username' ?")
                            return
                        else: # No recognized intent
                            self.__text_action("I'm sorry, I don't know about that yet.\n Are you sure about '"+self.username+"'?")
                            return

                    if self.state == float(add_user_state) + 0.4:

                        if text:
                            self.new_user.password == text
                            self.state = float(add_user_state) + 0.5
                            self.__text_action("are you sure about '"+text+"'?")
                            return
                        else:
                            self.__text_action("I'm sorry, I don't know about that yet.")
                            return

                    if self.state == float(add_user_state) + 0.5:

                        if intent == 'yes':
                            self.state = normal_state
                            self.__text_action("new user added")
                            self.knowledge.add_user(self.new_user)
                            self.new_user == None
                            return
                        elif intent == 'no':
                            self.state = float(add_user_state) + 0.4
                            self.__text_action("what is new users 'password' ?")
                            return
                        else: # No recognized intent
                            self.__text_action("I'm sorry, I don't know about that yet.")
                            return

            except Exception as e:
                print ("Failed wit!")
                print(e)
                traceback.print_exc()
                self.__text_action("I'm sorry, I couldn't understand what you meant by that")
                return

    def __joke_action(self):
        joke = self.nlg.joke()
        self.__text_action(joke)

    def __todo(self):
        todo = self.knowledge.todo()        
        self.__list_action(todo)

    def __note(self):
        notes = self.knowledge.note()
        self.__list_action(notes)

    def __currency(self):
        currency = self.knowledge.find_currency()
        if currency:
            
            self.__currency_action(currency)
        else:
            self.__text_action("I had some trouble finding currency rates for you")

    def text_action(self, text=None):
        self.__text_action(text)

    def __text_action(self, text=None):
        if text is not None:
            requests.get("http://localhost:8080", {"text": text} )
            self.speech.synthesize_text(text)
    
    def __list_action(self, listin=None):
        if listin is not None:
            requests.get("http://localhost:8080", {"list": "_".join(listin)} )
            for sentns in listin:
                self.speech.synthesize_text(sentns)  

    def __currency_action(self, currencyrates=None):
        if currencyrates is not None:
            requests.get("http://localhost:8080", {"currency": ','.join(str(v) for v in currencyrates)} )
            print()          

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
            self.__text_action("I had some trouble finding about "+q)

    def __weather_action(self, nlu_entities=None):

        weather_obj = self.knowledge.find_weather()
        weather_speech = self.nlg.weather(weather_obj)

        self.__list_action(weather_speech)

    def __maps_action(self,entities):

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
            requests.get("http://localhost:8080", {"image":(maps_url)} )
            self.speech.synthesize_text(maps_action)
        else:
            self.__text_action("I'm sorry, I couldn't understand what location you wanted.")

