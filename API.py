from flask import jsonify
from flask import Flask, request
from collections import namedtuple
from datetime import datetime, timedelta
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

import sys
import twitter
import requests
import json

app = Flask(__name__)

def extract_tweet(tweet):
	text = tweet.text
	created_at = tweet.created_at

	return {'text': text,
			'created_at': created_at}

def removeInvalidCharacters(string):
	charsToRemove = ['&', "'", '"', '#', '*', '!', '/'];
	for ch in charsToRemove:
		if ch in string:
			string = string.replace(ch, "");
			
	return string;
			
def twitterRequest(query):
	api = twitter.Api(consumer_key = "gMUVzhubG78H2o3HYWFY5csQQ",
					  consumer_secret = "Tc3M4vrraHni2vUWZH9PdeDdUhuHHqbIcpDy9OZjvIICcXgclS",
					  access_token_key = "984138848-PhpKudC6iLRjwLuU1LBbOH5hq4iknM3NoI7jcizL",
					  access_token_secret = "EHazGd0Xgx9LGFVxtKgwC5hVzLns7A8orJphSNn45CqKr");

	sinceDate = datetime.today() - timedelta(days=7);
	since = sinceDate.strftime("%Y-%m-%d");
	results = api.GetSearch(raw_query = 'q=' + query + '&since=' + since + '&count=100');
	tweets = [extract_tweet(tweet) for tweet in results]
	return json.dumps(tweets)

def parseTicketmasterJSONIntoObject(jsonString):
	data = json.loads(jsonString);
	try:
		eventList = data["_embedded"]["events"];
	except:
		return None;
	
	points = [];
	
	for i in range (0, len(eventList)):
		singleData = {};
		
		try:
			name = data["_embedded"]["events"][i]["name"];
			
			singleData["id"] = data["_embedded"]["events"][i]["id"];
			singleData["type"] = data["_embedded"]["events"][i]["type"];
			singleData["name"] = name;
			singleData["image_list"] = data["_embedded"]["events"][i]["images"][0]["url"];
			singleData["description"] = None;
			singleData["date"] = data["_embedded"]["events"][i]["dates"]["start"]["localDate"];
			singleData["time"] = data["_embedded"]["events"][i]["dates"]["start"]["localTime"];
			singleData["timeTBD"]  = data["_embedded"]["events"][i]["dates"]["start"]["timeTBA"];
			singleData["rating"] = None;
			singleData["rating_count"] = None;
			singleData["genre"] = data["_embedded"]["events"][i]["classifications"][0]["segment"]["name"]; 
			#singleData["price"] = data["_embedded"]["events"][i]["priceRanges"][0]["min"];
			singleData["latitude"] = data["_embedded"]["events"][i]["_embedded"]["venues"][0]["location"]["longitude"];
			singleData["longitude"]= data["_embedded"]["events"][i]["_embedded"]["venues"][0]["location"]["latitude"];
			#singleData["twitter"] = twitterRequest(removeInvalidCharacters(name)));
			singleData["link"] = data["_embedded"]["events"][i]["url"]
			
			points.append(singleData);
		except:
			print(str(singleData), file=sys.stderr);
		
	totalData = {};
	totalData = points;
	return str(totalData);
	
def parseAmadeusJSONIntoObject(jsonString):
	data = json.loads(jsonString);
	try:
		pointsOfInterest = data["points_of_interest"];
	except:
		return None;
	
	points = [];
		
	for i in range (0, len(pointsOfInterest)):
		singleData = {};
		
		try:
			name = data["points_of_interest"][i]["title"];
			
			singleData["id"] = None;
			singleData["type"] = "Attraction";
			singleData["name"] = name;
			singleData["image_list"] = data["points_of_interest"][i]["main_image"];		
			singleData["description"]= data["points_of_interest"][i]["details"]["short_description"];
			singleData["date"] = None;
			singleData["TimeTBD"] = None;
			singleData["rating"] = data["points_of_interest"][i]["grades"]["yapq_grade"];		
			singleData["rating_count"] = None;
			singleData["genre"] = None;
			#singleData["price"] = None;
			singleData["latitude"] = data["points_of_interest"][i]["location"]["latitude"];
			singleData["longitude"] = data["points_of_interest"][i]["location"]["longitude"];
			#singleData["twitter"] = twitterRequest(removeInvalidCharacters(name));
			singleData["link"] = data["points_of_interest"][i]["details"]["wiki_page_link"];
			
			points.append(singleData);
		except:
			print("FAIL: " + str(singleData), file=sys.stderr);
		
	totalData = {};
	totalData = points;
	return str(totalData);

def extract_business(business, attraction_type):
	id = business.id;
	type = attraction_type;
	name = business.name;
	image_list = business.image_url;
	description = business.snippet_text;
	date = None;
	time = None;
	timeTBD = None;
	rating = business.rating;
	rating_count = business.review_count;
	genre = business.categories;
	#price = ...
	latitude = business.location.coordinate.latitude;
	longitude = business.location.coordinate.longitude;
	#twitter = twitterRequest(removeInvalidCharacters(name));
	link = business.url;

	return {'id': id,
			'type' : type,
			'name': name,
			'image_list': image_list,
			'description': description,
			'date' : date,
			'time' : time,
			'timeTBD' : timeTBD,
			'rating': rating,
			'rating_count': rating_count,
			'genre' : genre,
			'latitude': latitude,
			'longitude': longitude,
			'twitter' : twitter,
			'link' : link};	

# RETURNS OBJECT WITH AMADEUS DATA
@app.route("/amadeus")
def amadeusRequest():
	apikey = "JDe6GYa6Xf1WvmCcRJs39xHPL905xbOi";
	latitude = request.args.get("latitude");
	longitude = request.args.get("longitude");
	radius = request.args.get("radius");
	
	query = "https://api.sandbox.amadeus.com/v1.2/points-of-interest/yapq-search-circle?";
	query += "apikey=" + apikey;
	
	if (latitude != None and longitude != None and radius != None):
		query += "&latitude=" + latitude + "&longitude=" + longitude + "&radius=" + radius;
	
	query += "&social_media=true";
	
	r = requests.get(query);
	return parseAmadeusJSONIntoObject(r.text);

# RETURNS OBJECT WITH TICKETMASTER DATA
@app.route("/ticketmaster")
def ticketmasterRequest():
	apikey = "4b9Nw9xfcvfZQwmYpeof3PIo0uNWOQql";
	latitude = request.args.get("latitude");
	longitude = request.args.get("longitude");
	radius = request.args.get("radius");
	
	query = "https://app.ticketmaster.com/discovery/v2/events.json?";
	query += "apikey=" + apikey;
	
	if (latitude != None and longitude != None and radius != None):
		query += "&latlong=" + latitude + "," + longitude + "&radius=" + radius;
	
	r = requests.get(query);

	return parseTicketmasterJSONIntoObject(r.text);

# RETURNS OBJECT WITH YELP RESTAURANT DATA
@app.route("/restaurants")
def restaurants():
	latitude = request.args.get('latitude');
	longitude = request.args.get('longitude');
	
	auth = Oauth1Authenticator(
		consumer_key="niAZAbxG4R-zMR_BXSXCSg",
		consumer_secret="QLjZH_19u9unIyfQTK5-k18slzQ",
		token="s8ipQMaCxLziSJcVMbB1Nj20YYijfLpa",
		token_secret="3qsdQR53xxyQtUQMimHrXRvK2e0"
	)

	client = Client(auth);	
	
	params = {
		'term': 'food',
	}
	
	response = client.search_by_coordinates(latitude, longitude, **params);

	data = [extract_business(business, "restaurant") for business in response.businesses]
	return str(data);

# RETURNS OBJECT WITH YELP MUSEUM DATA
@app.route("/museums")
def museums():
	city = request.args.get('city')
	latitude = request.args.get('latitude');
	longitude = request.args.get('longitude');
	
	auth = Oauth1Authenticator(
		consumer_key="niAZAbxG4R-zMR_BXSXCSg",
		consumer_secret="QLjZH_19u9unIyfQTK5-k18slzQ",
		token="s8ipQMaCxLziSJcVMbB1Nj20YYijfLpa",
		token_secret="3qsdQR53xxyQtUQMimHrXRvK2e0"
	)

	client = Client(auth);	
	
	params = {
		'term': 'museum'
	}

	response = client.search_by_coordinates(latitude, longitude, **params);
	data = [extract_business(business, "museum") for business in response.businesses];
	return str(data);
	
if __name__ == "__main__":
	app.debug = True;
	app.run()
