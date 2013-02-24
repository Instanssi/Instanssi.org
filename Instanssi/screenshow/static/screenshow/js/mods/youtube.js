"use strict";

/*
 * Screenshow Youtube module
 * Author: Tuomas Virtanen
 */

function ScreenYoutube(settings, jmobj, obj, url, testurl) {
    this.settings = settings; 
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
    this.res_x = 1280;
    this.res_y = 720;
    
    /**
     * Initialize the player with a random video 
     */
    this.init = function() {
        this.obj.html('<div id="ytplayer" style="display: block;"></div>');
        this.player = $('#ytplayer');
        this.player.tubeplayer({
            width: this.res_x,
            height: this.res_y,
            allowFullScreen: "true",
            initialVideo: "M_eYSuPKP3Y",
            preferredQuality: "hd720",
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
        // Start playback.
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
     * the next video from the playlist when slide is shown. If, however, 
     * video playback is switched off from settings, restart the timer.
     */
    this.set_available = function() {
        if(this.settings.get('enable_videos')) {
            this.obj.data("stepData").exclude = false;
            this.jmobj.jmpress('reapply', this.obj);
        } else {
            this.timer = null;
            this.attempt_start_timer();
        }
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
     * Attempts to update the playlist from the server,
     * and handles possible timer timeout changes.
     */
    this.update = function() {
        // Handle timer time change
        var newtime = this.settings.get('video_interval') * 60 * 1000;
        if(newtime < 100) {
            newtime = 100; // minimum of 100 milliseconds.
        }
        if(newtime != this.video_interval) {
            this.video_interval = newtime;
            if(this.timer != null) {
                window.clearTimeout(this.timer);
                this.timer = null;
            }
        }
        
        // Request playlist changes
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
