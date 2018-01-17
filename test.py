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
			try:
				audio = recognizer.listen(source, 5, 12)
			except:
				pass
	try:
		return recognizer.recognize_google(audio)
	except Exception:
		pass
	#except speech_recognition.UnknownValueError:
	#	print("Couldn't understand")
	return ""

def qlisten():
	with speech_recognition.Microphone() as source:
			recognizer.adjust_for_ambient_noise(source)
			try:
				audio = recognizer.listen(source, 5, 5)
			except:
				pass
	try:
		return recognizer.recognize_google(audio)
#	except speech_recognition.UnknownValueError:
#		print("Couldn't understand")
	except Exception:
		pass
	return ""

def play(input, length):
	tts = gTTS(text = input, lang = 'en')
	tts.save("output.mp3")
	os.system("start output.mp3")
	time.sleep(length)

@app.route("/")
def hello():
	query = "Hi, Alexa, " + request.args.get("query")
	if '.' in query:
		query = "Hi, " + query.split(" Alexa,")[1]
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
		if '2' in numPeople:
			numPeople = "two people"
		if '4' in numPeople:
			numPeople = "four! people"
		#numPeople = numPeople.split("people")[0]
		test = test.split(" for ")[0]
		location = test.split(" at ")[1].replace(" ",". ") + ", Ann, Arbor"
		play("Hi, the " + location, 7)
		right = False
		while right == False:
			print("Location selection")
			result = qlisten()
			print(result)
			if "people" in result:
				print("Location confirmed")
				right = True
			#elif result == "":
			#	print("Didn't hear location")
			#	play("Hi, alexa, the " + location, 3)
			#	result = qlisten()
			#	print(result)
			else:
				print("Didn't hear location correctly")
				play("Hi, alexa, the " + location, 4)


		
		right = False
		while right == False:
			play("Hi, " + numPeople, 3)
			print("Number of People")
			result = qlisten()
			print(result)
			if "party" in result or "people" in result:
				print("Didn't hear number of people correctly")
				#play("Hi, " + numPeople, 3)
			elif result == "":
				print("Didn't hear number of people")
				result = qlisten()
				print(result)
			elif "date" in result:
				print("Number of people confirmed")
				right = True
			else:
				print("Number of people confirmed")
				right = True
			
		play("Hi, alexa, " + date, 8)
		right = False
		while right == False:
			print("Date selection")
			result = qlisten()
			print(result)
			if "date" in result or "day" in result or "reservation" in result:
				print("Didn't hear date correctly")
				play("Hi, alexa, " + date, 3)
			elif result == "":
				print("Didn't hear date")
				result = qlisten()
				print(result)
				play("Hi, alexa, " + date, 3)
			else:
				print("Date confirmed")
				right = True
		play("Hi, alexa, " + resTime, 3)

		
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