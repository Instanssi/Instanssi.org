"use strict";

/*
 * Screenshow Youtube module
 * Author: Tuomas Virtanen
 */

var _youtube_ready = false;
function onYouTubePlayerReady(id) {
    _youtube_ready = true;
}

var _youtube_status = -1;
function onYoutubeStateChange(status) {
    _youtube_status = status;
}

function ScreenYoutube(jmobj, obj, url, testurl) {
    this.obj = obj;
    this.url = url;
    this.jmobj = jmobj;
    this.testurl = testurl;
    
    this.cache = [];
    this.timeout = 3000;
    this.position = 0;
    this.player = 0;
    
    this.init = function() {
        this.obj.html('<div id="popcorn" style="display: block;"></div>');
        this.obj.on('enterStep', $.proxy(this.start, this));
        this.obj.on('leaveStep', $.proxy(this.stop, this));
    }
    
    this.start = function() {
        // Get video
        var video = this.cache[this.position++];
        
        // Start playback
        if(this.player) {
            this.player.media.src = video.url;
            this.player.media.children[0].src = video.url;
            this.player.load();
        } else {
            this.player = Popcorn.youtube('#popcorn', video.url);
        }
        this.player.on('ended', $.proxy(this.done, this));
        this.player.play();
        
        console.log(this.player.media.src);
        
        // Start over if needed
        if(this.position >= this.cache.length) {
            this.position = 0;
        }
    }
    
    this.done = function() {
        this.jmobj.jmpress('next');
    }
    
    this.stop = function() {

    }

    this.fetch_success = function(data) {
        // Save received data to cache
        this.cache = data['playlist'];
        if(this.cache.length <= this.position) {
            this.position = 0;
        }
        
        // Disable if there are no videos
        if(this.cache.length == 0) {
            this.obj.data("stepData").exclude = true;
            this.jmobj.jmpress('reapply', this.obj);
        }
    }
    
    this.fetch_error = function(jqXHR, status, errorThrown) {
        console.log("Error while fetching video playlist!");
    }
    
    this.update = function() {
        $.ajax({ 
            url: this.url, 
            dataType: 'json', 
            success: $.proxy(this.fetch_success, this),
            timeout: this.timeout,
            type: 'GET',
            error: $.proxy(this.fetch_error, this)
        });
    }
}
