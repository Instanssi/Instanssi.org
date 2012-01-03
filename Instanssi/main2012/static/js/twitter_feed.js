// Original from stackoverflow
function parseTwitterDate(tdate) {
    var system_date = new Date(Date.parse(tdate));
    var user_date = new Date();
    if (K.ie) {
        system_date = Date.parse(tdate.replace(/( \+)/, ' UTC$1'))
    }
    var diff = Math.floor((user_date - system_date) / 1000);
    if (diff <= 5) { return "just now"; }
    if (diff < 60) { return "seconds ago"; }
    if (diff <= 70) { return "one minute ago"; }
    if (diff <= 3600-100) { return Math.round(diff / 60) + " minutes ago"; }
    if (diff <= 3600+100) { return "1 hour ago"; }
    if (diff <= 3600*11) { return Math.round(diff / 3600) + " hours ago"; }
    if (diff <= 3600*13) { return "1 day ago"; }
    if (diff < 3600*24*7) { return Math.round(diff / 86400) + " days ago"; }
    if (diff <= 3600*24*8) { return "1 week ago"; }
    if (diff <= 3600*24*7*4) { return "1 month ago"; }
    if (diff < 3600*24*365) { return Math.round(diff / (3600*24*7*4)) + " months ago"; }
    return "over a year ago";
}

// from http://widgets.twimg.com/j/1/widget.js
var K = function () {
    var a = navigator.userAgent;
    return {
        ie: a.match(/MSIE\s([^;]*)/)
    }
}();

(function($){
$.fn.twitterfeed = function(options) {
    var defaults = {
        username: ""
    };
    var options = $.extend(defaults, options);
    
    return this.each(function() {
        var obj = $(this);
        var url = 'https://api.twitter.com/1/statuses/user_timeline.json?count=5&screen_name='+options.username+'&callback=?&trim_user=1';
        $.getJSON(url, function(data) {
            var out = "";
            $.each(data, function(key, val) { 
                out += '<p class="feedelement">';
                out += val['text']+'<br />'+parseTwitterDate(val['created_at']);
                out += '</p>';
            }); 
            obj.append(out);
        });
    });
};
})(jQuery);