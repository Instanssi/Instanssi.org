'use strict';

$(function() {
    var calid = "46oohofs0emt0rrm05darkobdo@group.calendar.google.com";
    var apik = "AIzaSyAnSBTmLepfcMtJoft8foXhstAv7PpYTos";
    var calurl = "https://www.googleapis.com/calendar/v3/calendars/" + calid + "/events?key=" + apik + "&timeMin=2019-02-20T10:00:00%2B02:00";
    var wds = ['Sunnuntai', 'Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai'];

    function onPageLoad() {
        calRequest();
        setInterval(calRequest, 15000);
    }

    function parseCal(params) {
        var oldDay = '';
        var dateNow = new Date().toISOString();

        var newData = params.sort(function(a, b) {
            return (a.start.dateTime > b.start.dateTime) - (b.start.dateTime > a.start.dateTime);
        });

        var output = "";
        $.each(newData, function(i, val) {
            var startD = new Date(val.start.dateTime);
            var day = startD.getDate();
            var endD = new Date(val.end.dateTime);
            var description = '<small>' + val.description + '</small>';
            var startHour = startD.getHours() < 10 ? '0'+ startD.getHours() : startD.getHours();
            var endHour = endD.getHours() < 10 ? '0' + endD.getHours() : endD.getHours();
            var startMinutes = startD.getMinutes() === 0 ? '00' : startD.getMinutes();
            var endMinutes = endD.getMinutes() === 0 ? '00' : endD.getMinutes();

            var month = startD.getMonth() + 1;
            var weekday = wds[startD.getDay()];
            var dateStr = weekday + ' ' + day + '.' + month + '.';
            var startTimeStr = startHour + ':' + startMinutes;
            var endTimeStr = endHour + ':' + endMinutes +'<br>';
            var timeStr = '<b>' + startTimeStr + '-' + endTimeStr+'</b>';
            if (dateStr !== oldDay) {
                output += '<h3>' + dateStr + '</h3>';
            }
            output += '<p>'+ timeStr + ' ' + val.summary + ': ' + description + '</p>';
            if (dateNow > val.start.dateTime && dateNow < val.end.dateTime) {
                output += '<p class="nytsoi">'+ timeStr + ' ' + val.summary + ': ' + description + '</p>';
            }
            oldDay = dateStr;
        });
        $('#aikataulu').html(output);
    }

    function calRequest() {
        $.ajax({
            url: calurl,
            type: 'GET',
            cache: false,
            dataType: 'jsonp',
            timeout: 3000,
            success: function(data, status, jqXHR) {
                if (status === 'error') {
                    console.log('Ei saatu kalenterin tietoja.');
                    return;
                }
                parseCal(data.items);
            }
        });
    }

    onPageLoad();
});