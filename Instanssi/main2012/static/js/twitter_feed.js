// Widget by bebraw, from https://github.com/bebraw/codegrove-site/blob/gh-pages/js/index.js
// Some small modifications by Katajakasa

function attr(k, v) {
    // http://stackoverflow.com/questions/2010892/storing-objects-in-html5-localstorage
    var target = sessionStorage;

    if(!target) {
        return null; // no support for localStorage :(
    }
  
    if(v !== undefined) {
        target.setItem(k, JSON.stringify(v));
        return null;
    }
        
    try {
        return JSON.parse(target.getItem(k));
    }
    catch(e) {}
    
    return target.getItem(k);
}

function orderEntries(entries, limit) {
    entries.sort(function(a, b) {
        return a.publishedDate < b.publishedDate? 1: -1;
    });
    return entries.slice(0, limit);
}

function ISODateString(d){
    function pad(n){
        return n<10 ? '0'+n : n;
    }
    return d.getUTCFullYear()+'-' +
        pad(d.getUTCMonth()+1)+'-'+
        pad(d.getUTCDate());
}

// https://github.com/jamescarr/jquery-text-tools
function linkify(text){
    return text.replace(/(href="|<a.*?>)?[A-Za-z]+:\/\/[A-Za-z0-9-_]+\.[A-Za-z0-9-_:%&\?\/.=]+/g, function($0, $1) {
        return $1 ? $0 : $0.link($0);
    });
}

function getLatestTweets(user, limit, doneCb) {
    var count = 0;
    var tweetCache = attr('tweetCache');
    var now = new Date();

    if(tweetCache) {
        if(new Date(now - new Date(tweetCache.time)).getHours() < 1) {
            var tweets = tweetCache.tweets;

            tweets = $.map(tweets, function(k, i) {
                k.publishedDate = new Date(k.publishedDate);
                return k;
            });

            doneCb(tweets);
            return;
        }
    }
    else {
        tweetCache = {
            time: now.getTime()
        };
    }

    twitterlib.timeline(user, { limit: limit }, function(tweets) {
        var ret = [];
    
        $.each(tweets, function(i, k) {
            ret.push({
                author: user,
                text: linkify(k.text),
                publishedDate: k.created_at
            });
        });

        tweetCache.tweets = ret;
        attr('tweetCache', tweetCache);

        ret = $.map(ret, function(k, i) {
            k.publishedDate = new Date(k.publishedDate);
            return k;
        });
    
        doneCb(ret);
    });
}

function constructTweetUI($parent, entries) {
    var $dl = $('<dl>').appendTo($parent);

    $.each(entries, function(i, k) {
        $('<dt>').append('<span class="date">' + ISODateString(k.publishedDate) + '</span>').
            append('<span class="author">' + k.author + '</span>').appendTo($dl);
        $('<dd>').append('<span class="title">' + k.text + '</span>').appendTo($dl);
    });
}

function twitterWidget($parent, users, amount) {
    var parsedData = [];
    var found = 0;

    $.each(users, function(i, user) {
        getLatestTweets(user, 3, function(data) {
            parsedData = parsedData.concat(data);
            found++;
      
            if(found == users.length) {
                var entries = orderEntries(parsedData, amount);
                constructTweetUI($parent, entries);
            }
        });
    });
}

// Hax.
(function($){
$.fn.twitterfeed = function(options) {
    var defaults = {
        users: [],
        tweetcount: 5
    };
    var options = $.extend(defaults, options);
    
    return this.each(function() {
        twitterWidget($(this), options.users, options.tweetcount); 
    });
};
})(jQuery);

