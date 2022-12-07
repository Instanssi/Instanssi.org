"use strict";

/*
 * Screenshow Messages module
 * Author: Tuomas Virtanen
 */

function ScreenMessages(settings, jmobj, obj, url) {
    this.settings = settings; 
    this.obj = obj;
    this.url = url;
    this.jmobj = jmobj;
    
    this.timeout = 3000;
    this.cache = [];
    this.content_obj = 0;
    this.run = false;
    this.showing = 0;
    
    this.init = function() {
        this.obj.html('<p id="message_content"></p>');
        this.content_obj = $('#message_content');
    }
    
    this.post_init = function() {
        this.obj.on('enterStep', $.proxy(this.start, this));
        this.obj.on('leaveStep', $.proxy(this.stop, this));
    }
    
    this.fetch_success = function(data) {
        // Save to cache
        this.cache = data['messages'];
        
        // Set jmpress stuff
        this.obj.data("stepData").exclude = (this.cache.length === 0);
        this.obj.data("stepData").duration = this.cache.length * 5000;
        this.jmobj.jmpress('reapply', this.obj);
    }
    
    this.fetch_error = function(jqXHR, status, errorThrown) {
        console.log("There was a problem while fetching message data.");
        this.obj.data("stepData").exclude = (this.cache.length === 0);
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
    
    this.viewchain = function() {
        if(!this.run) {
            return;
        }
        if(this.showing >= this.cache.length) {
            return;
        }
        this.content_obj.html(this.cache[this.showing]);
        this.content_obj.fadeIn(1000).delay(3000).fadeOut(1000, $.proxy(this.viewchain, this));
        this.showing++;
    }
    
    this.start = function() {
        this.run = true;
        this.showing = 0;
        this.viewchain();
    }
    
    this.stop = function() {
        this.run = false;
    }
}
