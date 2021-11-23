'use strict';

$(function() {
    var calid = '46oohofs0emt0rrm05darkobdo@group.calendar.google.com';
    var apik = 'AIzaSyAnSBTmLepfcMtJoft8foXhstAv7PpYTos';     // pub
    var sheetid = '1pRBIrNYjw5Qp1B8DyiyeKhFPFZB0hS_L94d4pa6V6YU';

    var datarange = escape('Musiikki!A2:D2');
    var sheeturl = 'https://sheets.googleapis.com/v4/spreadsheets/' + sheetid + '/values/' + datarange + '?key=' + apik;
    var calurl = 'https://www.googleapis.com/calendar/v3/calendars/' + calid + '/events?key=' + apik + '&timeMin=2021-02-20T10:00:00%2B02:00&timeMax=2021-05-20T10:00:00%2B02:00';
    var wds = ['Sunnuntai', 'Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai'];

    var oldval = '';

    function lpad(number, digits) {
        return Array(Math.max(digits - String(number).length + 1, 0)).join('0') + number;
    }

    function parseCal(params) {
        var oldDay = '';
        var dateNow = new Date().getTime();

        var newData = params.sort(function(a, b) {
            return (a.start.dateTime > b.start.dateTime) - (b.start.dateTime > a.start.dateTime);
        });

        var output = '';
        $.each(newData, function(i, val) {
            var startD = new Date(val.start.dateTime);
            var day = startD.getDate();
            var endD = new Date(val.end.dateTime);
            var description = '<small>' + val.description + '</small>';

            var startHour = lpad(startD.getHours(), 2);
            var endHour = lpad(endD.getHours(), 2);
            var startMinutes = lpad(startD.getMinutes(), 2);
            var endMinutes = lpad(endD.getMinutes(), 2);

            var month = startD.getMonth() + 1;
            var weekday = wds[startD.getDay()];
            var dateStr = weekday + ' ' + day + '.' + month + '.';
            var startTimeStr = startHour + ':' + startMinutes;
            var endTimeStr = endHour + ':' + endMinutes + '<br>';
            var timeStr = '<b>' + startTimeStr + '-' + endTimeStr + '</b>';

            if (dateStr !== oldDay) {
                output += '<h3>' + dateStr + '</h3>';
            }

            if (dateNow > startD && dateNow < endD) {
                output += '<p style="background-color: #eee;">' + timeStr + ' ' + val.summary + ': ' + description + '</p>';
            } else {
                output += '<p>' + timeStr + ' ' + val.summary + ': ' + description + '</p>';
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
                if (typeof data !== 'undefined' && typeof data.items !== 'undefined') {
                    parseCal(data.items);
                }
            },
            complete: function() {
                setTimeout(calRequest, 300000);     // 5 mins
            }
        });
    }

    function parseSheet(params) {
        var updateStr = '';
        if (params[1] !== '') {
            // Kun Ohjelma -kenttä annettu
            if (typeof params[2] !== 'undefined' && params[2] !== '' && typeof params[3] !== 'undefined' && params[3] !== '') {
                // Jos lähetyksessä artisti & kappale -tiedot kummatkin
                updateStr += params[1] + ': ' + params[2] + ' - ' + params[3];
            } else if (typeof params[3] !== 'undefined' && params[3] !== '') {
                // Jos lähetyksessä kappale -tiedot (kun striimataan esim. Traktorilla).
                updateStr = params[1] + ': ' + params[3];
            } else {
                // Jos lähetyksessä ei näy artisti & kappale -tietoja.
                updateStr = params[1];
            }
        } else if (typeof params[2] !== 'undefined' && params[2] !== '' && typeof params[3] !== 'undefined' && params[3] !== '') {
            // Jos musa tulee radion omasta playlististä
            updateStr = params[2] + ' - ' + params[3];
        } else if (typeof params[2] !== 'undefined' && params[2] !== '') {
            // Jos vain artisti -tieto.
            updateStr = params[2];
        } else if (typeof params[3] !== 'undefined' && params[3] !== '') {
            // Jos vain kappale -tieto.
            updateStr = params[3];
        } else {
            // Kun metatietoja ei saatavilla lainkaan
            // updateStr = 'Tuntematon.';
        }

        if (updateStr !== oldval) {
            $('#radiostream_nytsoi').html(updateStr);
            oldval = updateStr;
        }
    }

    function sheetRequest() {
        $.ajax({
            url: sheeturl,
            type: 'GET',
            cache: false,
            dataType: 'jsonp',
            timeout: 3000,
            success: function(data, status, jqXHR) {
                if (status === 'error') {
                    console.log('Ei saatu taulukon tietoja.');
                    return;
                }
                if (typeof data !== 'undefined' && typeof data.values !== 'undefined') {
                    parseSheet(data.values[0]);
                }
            },
            complete: function() {
                setTimeout(sheetRequest, 15000);    // 15 sec
            }
        });
    }

    calRequest();
    sheetRequest();
});
