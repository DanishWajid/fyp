import random
import datetime


class NLG(object):
    """
    Used to generate natural language.
    """
    def __init__(self, user_name=None):
        self.user_name = user_name


    def joke(self):
        jokes = [
            "Artificial intelligence is no match for natural stupidity.",
            "A recent study has found that women who carry a little extra weight live longer than the men who mention it.",
            "I can totally keep secrets. It's the people I tell them to that can't.",
            "I started out with nothing, and I still have most of it.",
            "I used to think I was indecisive, but now I'm not too sure.",
            "Regular naps prevent old age, especially if you take them while driving.",
            "Take my advice. I'm not using it."
        ]

        return random.choice(jokes)

    def weather(self, in_dict):

        sentence1 = "The current temperature is " + str(in_dict["temperature"]) + " fahrenheit"
        sentence2 = "The windSpeed is " + str(in_dict["windSpeed"])
        sentence3 = "The forecast for today is " + str(in_dict["current_forecast"])
        
        ret_phrase = [sentence1,sentence2,sentence3]
        return ret_phrase

    def appreciation(self):
        phrases = [
            "No problem!",
            "Any time",
            "You are welcome",
            "You're welcome",
            "Sure, no problem",
            "Of course",
            "Don't mention it",
            "Don't worry about it"
        ]

        return random.choice(phrases)