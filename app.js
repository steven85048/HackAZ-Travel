$.(document).ready(function() {
	
	var submitButton = document.getElementById("#submit");
	submitButton.addEventListener('click', function() {
		var attractions = [];
		
		if ($('#museum').is(":checked")
			attractions.push("museum");
		if ($('#sports').is(":checked")
			attractions.push("sports");
		if ($('#music').is(":checked")
			attractions.push("music");
		
		
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
			
			for (var i = 1 ; i < totalArray.length; i++) 
				createConnectionBetweenPoints(totalArray[i-1], totalArray[i]);
			
		});
	});
});

function createConnectionBetweenPoints(var activityA, var activityB){
	var aLatitude = activityA.lat;
	var aLongitude = activityA.long;
	
	var bLatitude = activityB.lat;
	var bLongitude = activityB.long;
}

function appendArray(var mainArray, var arrayToAdd)
	for (var i = 0 ; i < arrayToAdd.length; i++) {
		mainArray.push(arrayToAdd[i]);
}

function getDataFromServer (var attraction, var latitude, var longitude, var cb){
	var xhr = new XMLHttpRequest();
	
	var url = "localhost:5000/activities?" + "attraction=" + attraction
			   + "&latitude=" + latitude + "&longitude=" + longitude;
	
	xhr.onload = function() {
		var response = xhr.responseText;
		var jsonResponse = JSON.parse(response);
		cb(jsonResponse);
	}
	xhr.open("GET", url);

	xhr.send();
}