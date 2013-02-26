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
                author: k.user.screen_name,
                text: twitterlib.ify.clean(twitterlib.expandLinks(k)),
                time: twitterlib.time.relative(k.created_at),
                tid: k.id_str,
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
    $parent.hide();
	
	var out = '<ul>';
    $.each(entries, function(i, k) {
        out += '<li>';
        out += '<span class="author">@'+k.author+': </span>';
        out += '<span class="text">'+k.text+'</span><br />';
        out += '<span class="time">'+k.time+'</span> &middot; ';
        out += '<span class="link"><a href="http://twitter.com/'+k.author+'/status/'+k.tid+'">Lue twitterissä »</a></span>';
        out += '</li>';
    });
    out += '</ul>';
    $parent.append(out).fadeIn( 500 );
}

function twitterWidget($parent, user, amount) {
    getLatestTweets(user, amount, function(data) {
        console.log(data);
        constructTweetUI($parent, data);
    });
}

// Hax.
(function($){
$.fn.twitterfeed = function(options) {
    var defaults = {
        user: '',
        tweetcount: 5
    };
    var options = $.extend(defaults, options);
    
    return this.each(function() {
        twitterWidget($(this), options.user, options.tweetcount); 
    });
};
})(jQuery);

