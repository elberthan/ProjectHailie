from flask import Flask
from flask import *
from gtts import gTTS
import requests
import os
import time
import json
import speech_recognition
from lyft_rides.auth import ClientCredentialGrant
from lyft_rides.session import Session
from lyft_rides.client import LyftRidesClient
from lyft_rides.auth import AuthorizationCodeGrant
from collections import OrderedDict
app = Flask(__name__)

recognizer=speech_recognition.Recognizer()

previous="none"
google_api_key = "AIzaSyDdTN3UIbvITjQiJQySsDl8OrJJx9gn4sk"

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

lyft_lat_start = -1
lyft_lng_start = -1
lyft_lat_end = -1
lyft_lng_end = -1
ride_id = -1
credentials = ""
auth_flow = AuthorizationCodeGrant(
    		"fFrmpOjzJ-ve",
    		"UculQOrXxkJf2J7USh8MKpUrXFqSu-fz",
    		{'public', 'rides.request', 'rides.read'},
    	)
client = ""
credentials = ""

@app.route("/lyft")
def lyft():
	global client
	global credentials
	session = auth_flow.get_session(request.url)
	client = LyftRidesClient(session)
	credentials = session.oauth2credential
	response = client.get_ride_types(lyft_lat_start, lyft_lng_start)
	ride_types = response.json.get('ride_types')
	options = "Options: \n"
	print("Options: ")
	for x in range(0, len(ride_types)):
		print(ride_types[x]["ride_type"])
		options = options + "--" + ride_types[x]["ride_type"] +"--" + "\n"
	return options

	

@app.route("/")
def hello():
	query = "Hi, Alexa, " + request.args.get("query")
	if 'lyft' in query or "Lyft" in query:
		if "call" in query or "order" in query:
			if "to" not in query or "from" not in query:
				return "Please include origin and destination addresses using 'to' and 'from'."
			destination = query.split(" to ")[1]
			query = query.split(" to ")[0]
			start = query.split(" from ")[1]
			r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address="+
				start +
				"&key=AIzaSyDdTN3UIbvITjQiJQySsDl8OrJJx9gn4sk")
			result = json.loads(r.content)
			global lyft_lat_start
			global lyft_lng_start
			lyft_lat_start = result["results"][0]["geometry"]["location"]["lat"]
			lyft_lng_start = result["results"][0]["geometry"]["location"]["lng"]

			r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address="+
				destination +
				"&key=AIzaSyDdTN3UIbvITjQiJQySsDl8OrJJx9gn4sk")
			result = json.loads(r.content)
			global lyft_lat_end
			global lyft_lng_end
			lyft_lat_end = result["results"][0]["geometry"]["location"]["lat"]
			lyft_lng_end = result["results"][0]["geometry"]["location"]["lng"]
			
			if not credentials:
				auth_url = auth_flow.get_authorization_url()
				return "Please authenticate: \n" + auth_url
			else:
				response = client.get_cost_estimates(lyft_lat_start, lyft_lng_start, lyft_lat_end, lyft_lng_end)
				ride_types = response.json.get('cost_estimates')
				print(ride_types)
				#print("Options: ")
				for x in range(0, len(ride_types)):
					print(ride_types[x]["ride_type"])
					if (ride_types[x]["ride_type"] == "lyft"):
						cost = ride_types[x]["estimated_cost_cents_max"]/100
						primetime = ride_types[x]["primetime_percentage"]
						duration = format(ride_types[x]["estimated_duration_seconds"]/60, '.1f')
						return "Estimated cost: $" + str(cost) + "\nPrimetime percentage: " + primetime + "\nEstimated duration: " + str(duration) + "\nConfirm ride?"
		if "confirm" in query or "yes" in query:
			response = client.request_ride("lyft", lyft_lat_start, lyft_lng_start, "none", lyft_lat_end, lyft_lng_end)
			global ride_id
			ride_id = response.json.get('ride_id')
			accepted = False
			args = {
            	"status": "accepted"
        	}
			endpoint = 'v1/sandbox/rides/{}'.format(ride_id)
			client._api_call('PUT', endpoint, args=args)
			while accepted == False:
				response = client.get_ride_details(ride_id)
				status = response.json.get('status')
				print(status)
				if status != "pending":
					accepted = True
			eta = format(response.json.get('origin')["eta_seconds"]/60, '.1f')
			model = response.json.get('vehicle')["model"]
			color = response.json.get('vehicle')["color"]
			license = response.json.get('vehicle')["license_plate"]
			name = response.json.get('driver')["first_name"]
			number = response.json.get('driver')["phone_number"]
			return "Confirmed. Calling the Lyft for you now. It should be outside in about "+str(eta)+" minutes. Look for a " + color + " " + model + " with license plate " + license + "." + " Your driver is " + name + ", and their number is " + number + "."
		if "check" in query or "status" in query or "where's" in query or "where" in query:
			accepted = False
			while accepted == False:
				response = client.get_ride_details(ride_id)
				status = response.json.get('status')
				if status != "pending":
					accepted = True
			eta = format(response.json.get('origin')["eta_seconds"]/60, '.1f')
			model = response.json.get('vehicle')["model"]
			color = response.json.get('vehicle')["color"]
			license = response.json.get('vehicle')["license_plate"]
			return "Status: " + status + "\nYour lyft should be outside in about "+str(eta)+" minutes. Look for a " + color + " " + model + " with license plate " + license + "."
		if "cancel" in query: 
			response = client.cancel_ride(ride_id)
			return "Ride cancelled."
			
		
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