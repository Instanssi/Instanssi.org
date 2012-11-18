"use strict";

/*
 * Screenshow Youtube module
 * Author: Tuomas Virtanen
 */

function ScreenYoutube(jmobj, obj, url, testurl) {
    this.obj = obj;
    this.url = url;
    this.jmobj = jmobj;
    this.testurl = testurl;
    
    this.cache = [];
    this.timeout = 3000;
    this.position = 0;
    this.player = null;
    this.timer = null;
    this.video_interval = 5*60*1000; // 5 minutes
    
    /**
     * Initialize the player with a random video 
     */
    this.init = function() {
        this.obj.html('<div id="ytplayer" style="display: block;"></div>');
        this.player = $('#ytplayer');
        this.player.tubeplayer({
            width: 1920,
            height: 1080,
            allowFullScreen: "true",
            initialVideo: "DeumyOzKqgI",
            preferredQuality: "hd1080",
            iframed: true,
            onPlayerEnded: $.proxy(function() {
                this.jmobj.jmpress('next');
            }, this)
        });
    }
    
    /**
     * Initialize jmpress related stuff. 
     */
    this.post_init = function() {
        this.obj.data("stepData").exclude = true;
        this.jmobj.jmpress('reapply', this.obj);
        this.obj.on('enterStep', $.proxy(this.start, this));
        this.obj.on('leaveStep', $.proxy(this.stop, this));
    }
    
    /**
     * Parses the code part from embedded youtube url.
     */
    this.parse_url = function(url) {
        var code = url;
        if(code[code.length-1] == '/') {
            code = code.substring(0, code.length-1);
        }
        code = code.substring(code.lastIndexOf('/')+1);
        return code;
    }
    
    /**
     * Pick the next video from the playlist and start playing it. 
     */
    this.start = function() {
        // Get video
        var video = this.cache[this.position++];
        this.player.tubeplayer('play', this.parse_url(video.url));
        
        // Start over if needed
        if(this.position >= this.cache.length) {
            this.position = 0;
        }
    }
    
    /**
     * Make the video slide invisible and attempt to restart the timer. 
     */
    this.stop = function() {
        this.obj.data("stepData").exclude = true;
        this.jmobj.jmpress('reapply', this.obj);
        this.timer = null;
        this.attempt_start_timer();
    }

    /**
     * Timer hit. Make video available. this.play will automatically pick
     * the next video from the playlist when slide is shown. 
     */
    this.set_available = function() {
        this.obj.data("stepData").exclude = false;
        this.jmobj.jmpress('reapply', this.obj);
    }
    
    /**
     * Handle timer
     * - If cache has items, and timer is already on, do nothing.
     * - If cache has items, but timer is not on, start it
     * - If cache has no items, kill timer.
     */
    this.attempt_start_timer = function() {
        if(this.cache.length > 0) {
            if(this.timer == null) {
                this.timer = setTimeout($.proxy(this.set_available, this), this.video_interval);
            }
        } else {
            if(this.timer != null) {
                window.clearTimeout(this.timer);
            }
            this.timer = null;
        }
    }

    /**
     * If the JSON playlist request was successful, this will be executed.
     * Save cache, handle position changes and attempt to start playback timer. 
     */
    this.fetch_success = function(data) {
        // Save received data to cache
        this.cache = data['playlist'];
        if(this.cache.length <= this.position) {
            this.position = 0;
        }
        
        this.attempt_start_timer();
    }
    
    /**
     * Handle playlist fetch errors. 
     */
    this.fetch_error = function(jqXHR, status, errorThrown) {
        console.log("Error while fetching video playlist!");
    }
    
    /**
     * Attempts to update the playlist from the server. 
     */
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
