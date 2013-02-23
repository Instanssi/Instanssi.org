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
    this.run = false;
    
    this.init = function() {}
    
    this.post_init = function() {
        this.obj.on('enterStep', $.proxy(this.start, this));
        this.obj.on('leaveStep', $.proxy(this.stop, this));
    }
    
    this.render = function(data) {
        // Write HTML from cache
        var output = '';
        $.each(this.cache, function(key, value) {
            output += '<p>';
            output += value['artist'];
            output += ' &middot; ';
            output += value['title'];
            output += '</p>';
            console.log(value);
        });
        this.obj.html(output);
    }
    
    this.fetch_success = function(data) {
        // Save to cache
        this.cache = data['playlist'];
        this.render();
        
        // Set jmpress stuff
        is_stopped = false
        if(this.cache.length > 0) {
            is_stopped = (this.cache[0]['state'] == 1);
        }
        this.obj.data("stepData").exclude = (this.cache.length == 0 || is_stopped);
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
