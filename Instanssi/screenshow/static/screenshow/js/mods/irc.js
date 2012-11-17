"use strict";

/*
 * Screenshow IRC module
 * Author: Tuomas Virtanen
 */

function ScreenIrc(jmobj, obj, url) {
    this.obj = obj;
    this.url = url;
    this.jmobj = jmobj;
    
    this.timeout = 3000;
    this.updatefreq = 1000;
    this.run = false;
    this.cache = [];
    this.timer = 0;
    this.last_id = 0;
    this.lines_per_screen = 24; // Screen can fit about 26 lines of text
    this.chars_per_line = 100; // Screen can fit about 100 characters per line
    
    this.init = function() {
        this.obj.on('enterStep', $.proxy(this.start, this));
        this.obj.on('leaveStep', $.proxy(this.stop, this));
    }
    
    this.display_cache = function() {
        var lines = 0;
        var i = 0;
        
        // Try to render the screen full of text, but not too full :)
        for(i = this.cache.length-1; i > 0; i--) {
            var text_len = this.cache[i]['text'].length;
            var nick_len = this.cache[i]['nick'].length;
            var estimated_lines = Math.floor( (text_len + nick_len + 9) / this.chars_per_line) + 1;
            if( (lines + estimated_lines) > this.lines_per_screen) {
                break;
            }
            lines += estimated_lines;
        }
        
        // Drop old cache entries by slicing up only those we need.
        this.cache = this.cache.slice(i);
        
        // Write HTML from cache
        var output = '<p id="ircheader">#instanssi @ IRCNet</p>';
        $.each(this.cache, function(key, value) {
            output += '<p><span class="irctime">';
            output += value['time'];
            output += '</span> <span class="ircnick">&lt;';
            output += value['nick'];
            output += '&gt;</span> ';
            output += value['text'];
            output += '</p>';
        });
        this.obj.html(output);
    }
    
    this.fetch_success = function(data) {
        // Read data fron JSON, and dump it to cache
        var size = data['log'].length;
        if(size > 0) {
            this.last_id = data['log'][size-1]['id'];
            this.cache = this.cache.concat(data['log']);
            this.display_cache();
        }

        // Check if we want to show the irc slide
        this.obj.data("stepData").exclude = (this.cache.length == 0);
        this.jmobj.jmpress('reapply', this.obj);
        
        // Start the timer again
        this.init_timer();
    }
    
    this.fetch_error = function(jqXHR, status, errorThrown) {
        // Dump error message to console and restart the timer
        console.log("There was a problem while fetching IRC data.");
        this.init_timer();
    }
    
    this.update = function() {
        $.ajax({ 
            url: this.url, 
            dataType: 'json', 
            success: $.proxy(this.fetch_success, this),
            data: { 'last_id': this.last_id },
            type: 'GET',
            timeout: this.timeout,
            error: $.proxy(this.fetch_error, this)
        });
    }
    
    this.init_timer = function() {
        window.clearTimeout(this.timer);
        if(this.run) {
            this.timer = setTimeout($.proxy(this.update, this), this.updatefreq);
        }
    }
    
    this.start = function() {
        this.run = true;
        this.update();
    }
    
    this.stop = function() {
        this.run = false;
    }
}
