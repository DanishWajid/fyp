# speech.py
# speechrecognition, pyaudio, brew install portaudio
import speech_recognition as sr
import os
import requests
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

class Speech(object):
    def __init__(self):
        pass

    def google_speech_recognition(self, recognizer, audio):
        speech = None
        try:
            speech = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from internet")

        return speech

    def listen_for_audio(self):
        # obtain audio from the microphone
        r = sr.Recognizer()
        m = sr.Microphone()
        with m as source:
            r.adjust_for_ambient_noise(source)
            print("I'm listening")
            requests.get("http://localhost:8080", {"prompt": "I'm listening"} )
            audio = r.listen(source)

        
        print ("Found audio")
        requests.get("http://localhost:8080", {"prompt": "Found audio"} )
        return r, audio

    def get_text(self, recognizer, audio):
        return self.google_speech_recognition(recognizer, audio)

    def synthesize_text(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save("tmp.mp3")
        song = AudioSegment.from_mp3("tmp.mp3")
        play(song)
        os.remove("tmp.mp3")