"use strict";

/*
 * Screenshow Twitter module
 * Author: Tuomas Virtanen
 */

function ScreenTwitter(jmobj, obj) {
    this.obj = obj;
    this.jmobj = jmobj;
    this.cache = [];
    
    this.init = function() {}
    
    this.post_init = function() {
        this.obj.on('enterStep', $.proxy(this.render, this));
    }
    
    this.render = function() {
        var out = '';
        $.each(this.cache, function(i, k) {
            out += '<div class="twittermsg">';
            out += '<span class="author">@'+k.author+': </span>';
            out += '<span class="message">'+k.text+'</span><br />';
            out += '<span class="time">&raquo; '+k.time+'</span>';
            out += '</div>';
        });
        this.obj.html(out);
    }
    
    this.handleTweets = function(tweets, options) {
        // Parse tweets
        var r = [];
        $.each(tweets, function(i, k) {
            r.push({
                author: k.user.screen_name,
                text: twitterlib.ify.clean(twitterlib.expandLinks(k)),
                time: twitterlib.time.relative(k.created_at),
                tid: k.id_str,
                publishedDate: k.created_at
            });
        });
        this.cache = r;
        
        // Check if we want to show the irc slide
        this.obj.data("stepData").exclude = (this.cache.length == 0);
        this.jmobj.jmpress('reapply', this.obj);
    }
    
    this.update = function() {
        twitterlib.timeline('Instanssi', { page: 1, limit: 5 }, $.proxy(this.handleTweets, this));
    }
}
