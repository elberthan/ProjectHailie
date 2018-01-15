from flask import Flask
from flask import *
from gtts import gTTS
import os
import time
import speech_recognition
app = Flask(__name__)

recognizer=speech_recognition.Recognizer()

previous="none"

def listen():
	with speech_recognition.Microphone() as source:
			recognizer.adjust_for_ambient_noise(source)
			audio = recognizer.listen(source, 5, 12)
	try:
		return recognizer.recognize_google(audio)
	except speech_recognition.UnknownValueError:
		print("Couldn't understand")
	return ""

def play(input, length):
	tts = gTTS(text = input, lang = 'en')
	tts.save("output.mp3")
	os.system("start output.mp3")
	time.sleep(length)

@app.route("/")
def hello():
	query = "Hi, Alexa, " + request.args.get("query")
	if "reservation" in query:
		play("Hi, Alexa, make a reservation", 7)
		test = request.args.get("query")
		location = ""
		numPeople = ""
		date = ""
		resTime = ""
		resTime = test.split(" around ")[1]
		test = test.split(" around ")[0]
		date = test.split(" on ")[1]
		test = test.split(" on ")[0]
		numPeople = test.split(" for ")[1]
		numPeople = numPeople.split("people")[0]
		test = test.split(" for ")[0]
		location = test.split(" at ")[1]
		play("Hi, " + location, 7)
		play("Hi, " + location, 7)
		play("Hi, " + numPeople, 5)
		play("Hi, " + date, 11)
		play("Hi, " + resTime, 3)
		
	else: 
		play(query, 3)
		
	print("Processing...")
	result = listen()
	print(result)
	return result

if __name__ == "__main__":
	app.run('0.0.0.0', port=8080)


#console.log("Alexa invocation detected");
#    var request = require('request');
#    request('http://localhost:8080/?query='+messageText, function(error, response, body){
#      console.log('error', error);
#      console.log('response', response && response.statusCode);
#      console.log('body', body);
#    });