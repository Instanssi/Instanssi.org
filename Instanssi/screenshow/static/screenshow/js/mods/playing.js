"use strict";

/*
 * Screenshow Messages module
 * Author: Tuomas Virtanen
 */

function ScreenNowPlaying(settings, jmobj, obj, url) {
    this.settings = settings; 
    this.obj = obj;
    this.url = url;
    this.jmobj = jmobj;
    
    this.timeout = 3000;
    this.cache = [];
    this.is_stopped = false;
    
    this.init = function() {}
    
    this.post_init = function() {
        this.obj.on('enterStep', $.proxy(this.start, this));
        this.obj.on('leaveStep', $.proxy(this.stop, this));
    }
    
    this.render = function(data) {
        // Write HTML from cache
        var output = '';
        var k = 0;
        $.each(this.cache, function(key, value) {
            if(k < 5 && value['state'] == 0) {
                output += '<p class="playing_song" style="color: #' +(k*2)+(k*2)+(k*2)+ ';">';
                if(k == 0) {
                    output += '&raquo; ';
                }
                output += value['artist'];
                output += ' &middot; ';
                output += value['title'];
                output += '</p>';
                k++;
            }
        });
        this.obj.html('<p class="playing_title">Toistossa:</p>' + output);
    }
    
    this.fetch_success = function(data) {
        // Save to cache
        this.cache = data['playlist'];
        this.render();
        
        // Set jmpress stuff
        if(this.cache.length > 0) {
            this.is_stopped = (this.cache[0]['state'] == 1);
            console.log(this.cache[0]);
        }
        this.obj.data("stepData").exclude = (this.cache.length == 0 || this.is_stopped);
        this.jmobj.jmpress('reapply', this.obj);
    }
    
    this.fetch_error = function(jqXHR, status, errorThrown) {
        console.log("There was a problem while fetching playlist data.");
        this.obj.data("stepData").exclude = (this.cache.length == 0);
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
