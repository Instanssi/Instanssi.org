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
        this.obj.html('<div id="ytplayer" style="display: block;"></div>');
        this.player = $('#ytplayer');
        this.player.tubeplayer({
            width: 1920,
            height: 1080,
            allowFullScreen: "false",
            initialVideo: "DeumyOzKqgI",
            preferredQuality: "hd1080",
            iframed: true,
            onStop: $.proxy(function() {
                this.jmobj.jmpress('next');
            }, this)
        });
        this.obj.on('enterStep', $.proxy(this.start, this));
        this.obj.on('leaveStep', $.proxy(this.stop, this));
    }
    
    this.parse_url = function(url) {
        var code = url;
        if(code[code.length-1] == '/') {
            code = code.substring(0, code.length-1);
        }
        code = code.substring(code.lastIndexOf('/')+1);
        return code;
    }
    
    this.start = function() {
        // Get video
        var video = this.cache[this.position++];
        this.player.tubeplayer('play', this.parse_url(video.url));
        
        // Start over if needed
        if(this.position >= this.cache.length) {
            this.position = 0;
        }
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
        this.obj.data("stepData").exclude = (this.cache.length == 0);
        this.jmobj.jmpress('reapply', this.obj);
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
