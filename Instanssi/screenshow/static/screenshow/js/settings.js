"use strict";

/*
 * Settings class
 * Author: Tuomas Virtanen
 */

function Settings(url) {
    this.url = url;
    this.timeout = 3000;
    this.timer = null;
    this.update_interval = 30000; // 30 sec
    this.data = {
        'enable_twitter': true,
        'enable_irc': true,
        'enable_videos': true,
        'video_interval': 5,
    };
    
    /**
     * A Simple getter for settings 
     */
    this.get = function(key) {
        return this.data[key];
    }
    
    /**
     * Fetches data from server 
     */
    this.update = function() {
        $.ajax({ 
            url: this.url, 
            dataType: 'json', 
            success: $.proxy(this.update_success, this),
            timeout: this.timeout,
            type: 'GET',
            error: $.proxy(this.update_failed, this)
        });
    }
    
    /**
     * Sets the timer for settings update 
     */
    this.wait = function() {
        this.timer = setTimeout($.proxy(this.update, this), this.update_interval);
    }
    
    /**
     * Settings update was successful. Cache settings, restart timer. 
     */
    this.update_success = function(data) {
        // If there was special settings on the server, use those. Otherwise go with the defaults
        if('settings' in data) {
            this.data = data['settings'];
        }
        this.wait();
    }
    
    /**
     * Settings update was a failure. Restart timer, use old settings. 
     */
    this.update_failed = function(jqXHR, status, errorThrown) {
        console.log("Failed to fetch settings from server!");
        this.wait();
    }
}
