$.(document).ready(function() {
	
	var submitButton = document.getElementById("#submit");
	var map = document.getElementById('#map'); 
	var searchBar = document.getElementById('#locationForm');
	
	mymap.on('click', function(var info) {
		searchBar.value = info.latlng;
	});
	
	submitButton.addEventListener('click', function() {
		var attractions = [];
		
		if ($('#museum').is(":checked")
			attractions.push("museum");
		if ($('#sports').is(":checked")
			attractions.push("sports");
		if ($('#music').is(":checked")
			attractions.push("music");
		
		var splitlatlong = (searchBar.value).split(",");
		var latitude = splitlatlong[0];
		var longitude = splitlatlong[1];
		
		getDataFromServer(attractions, latitude, longitude, function(var jsonResponse) {
			var morningActivities = jsonResponse.morning_activities;
			var afternoonActivities = jsonResponse.afternoon_activities;
			
			var morning = jsonResponse.morning;
			var lunch = jsonResponse.lunch;
			var dinner = jsonResponse.dinner;
			
			var totalArray = [];
			totalArray.push(morning);
			appendArray(totalArray, morningActivities);
			totalArray.push(lunch);
			appendArray(totalArray, afternoonActivities);
			totalArray.push(dinner);
			
			if (totalArray.length == 0){
				createNodeAtLatLong(totalArray[0].lat, totalArray[0].long);
				
				var lines = [];
				
				for (var i = 1 ; i < totalArray.length; i++) 
					lines.push(createConnectionBetweenPoints(totalArray[i-1], totalArray[i]));
				
				L.geoJSON(lines).addTo(map);
			} else 
				console.log("YOU HAVE FAILED!");
			
		});
	});
});

function createNodeAtLatLong(var latitude, var longitude){
	
}

function createConnectionBetweenPoints(var activityA, var activityB){
	var aLatitude = activityA.lat;
	var aLongitude = activityA.long;
	
	var bLatitude = activityB.lat;
	var bLongitude = activityB.long;
	
	createNodeAtLatLong(bLatitude, bLongitude);
	
	return {"type": "LineString",
			"coordinates": [[aLatitude, aLongitude], [ bLatitude, bLongitude]];
	}
}
function appendArray(var mainArray, var arrayToAdd)
	for (var i = 0 ; i < arrayToAdd.length; i++) {
		mainArray.push(arrayToAdd[i]);
}

function getDataFromServer (var attraction, var latitude, var longitude, var cb){
	var xhr = new XMLHttpRequest();
	
	var url = "hack-az.herokuapp.com/simulate?" + attraction
			   + "&lat=" + latitude + "&long=" + longitude;
	
	xhr.onload = function() {
		var response = xhr.responseText;
		var jsonResponse = JSON.parse(response);
		cb(jsonResponse);
	}
	xhr.open("GET", url);

	xhr.send();
}