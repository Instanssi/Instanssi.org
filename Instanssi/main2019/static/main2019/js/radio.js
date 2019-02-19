const apiurl = "/static/main2019/tests.txt";
const calid = "46oohofs0emt0rrm05darkobdo@group.calendar.google.com";
const apik = "AIzaSyAnSBTmLepfcMtJoft8foXhstAv7PpYTos";
const calurl = "https://www.googleapis.com/calendar/v3/calendars/" + calid + "/events?key=" + apik + "&timeMin=2019-02-20T10:00:00-02:00";
let titleline;
let title;
let caldata;
const wds = ['Sunnuntai', 'Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai'];

window.onload = onPageLoad();

function onPageLoad() {
    title = $('#stream_title').text;
	calRequest();
	let intervalli = setInterval(ajaxRequest, 10000);
}

function jsLongPoll() {

}

function parseCal(params) {
	var div = document.getElementById('aikataulu');
	
	var oldDay;
	var dateNow = new Date().toISOString();
	
	var newDatas = params.sort(function(a, b) {
		return (a.start.dateTime > b.start.dateTime) - (b.start.dateTime > a.start.dateTime);
	});

	jQuery.each(newDatas, function(i, val) {
		var startD = new Date(val.start.dateTime);
		var day = startD.getDate();
		var endD = new Date(val.end.dateTime);
		var description = '<small>'+val.description+ '</small>';
		var startHour = startD.getHours() < 10 ? '0'+ startD.getHours() : startD.getHours();
		var endHour = endD.getHours() < 10 ? '0' + endD.getHours() : endD.getHours();
		var startMinutes = startD.getMinutes() == 0 ? '00' : startD.getMinutes();
		var endMinutes = endD.getMinutes() == 0 ? '00' : endD.getMinutes();

		var month = startD.getMonth()+1;
		var weekday = wds[startD.getDay()];
		var dateStr = weekday + ' ' + day + '.' + month + '.';
		var startTimeStr = startHour + ':' + startMinutes;
		var endTimeStr = endHour + ':' + endMinutes +'<br>';
		var timeStr = '<b>' + startTimeStr + '-' + endTimeStr+'</b>';
		if (dateStr != oldDay) {
			div.innerHTML += '<h3>' + dateStr + '</h3>';
		}
		var putText = '<p>'+ timeStr + ' ' + val.summary + ': ' + description + '</p>';
		if (dateNow > val.start.dateTime && dateNow < val.end.dateTime) {
			putText = '<p class="nytsoi">'+ timeStr + ' ' + val.summary + ': ' + description + '</p>';
		}
		div.innerHTML += putText;
		oldDay = dateStr;
	})
}

function calRequest() {
	$.ajax({
		url: calurl,
		type: 'GET',
		cache: false,
		dataType: 'jsonp',
		timeout: 3000,
		success: function(data, status, jqXHR) {
			if (status == 'error') {
				console.log('Ei saatu kalenterin tietoja.');
				return;
			}
			var obj = data.items;
			parseCal(obj);
		},
		complete: function(jqXHR, status) {
			//console.log('complete, status: '+ status);
		}
	});
}

function ajaxRequest() {
	title = $('#stream_title').text();
    $.ajax({
        url: apiurl,
        type: 'GET',
        cache: false,
        //dataType: 'json',
        timeout: 3000,
        success: function(data, status, jqXHR) {
			if (status == 'error') {
				$('#stream_title').html('Ei saatu thietoja.');
			}
			if ($('#stream_title').html() == data) {
				return;
			}
			$('#stream_title').html(data.trim());
        },
		complete: function(jqXHR, status) {
			if (status == 'error') {
				$('#stream_title').html('Ei saatu tietoja.');
			}
        },
        fail: function(jqXHR, status, error) {
			console.log('fail: '+status);
			console.log('error: '+ error);
        },
        done: function(data, status) {
			console.log('done: '+status);
		}
    });
}
