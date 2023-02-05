"use strict";

/*
 * Screenshow Clock module
 * Author: Tuomas Virtanen
 */

function ScreenClock(settings, jmobj, obj) {
    this.settings = settings; 
    this.obj = obj;
    this.jmobj = jmobj;
    this.updatefreq = 1000;
    
    this.run = false;
    this.timer = 0;
    this.time_obj = 0;
    this.date_obj = 0;

    this.init = function() {
        this.obj.html('<p id="clock_time"></p><p id="clock_date"></p>');
        this.time_obj = $('#clock_time');
        this.date_obj = $('#clock_date');
    }
    
    this.post_init = function() {
        this.obj.on('enterStep', $.proxy(this.start, this));
        this.obj.on('leaveStep', $.proxy(this.stop, this));
    }

    this.update = function() {
        // Get times
        const now = new Date();
        const hour = now.getHours();
        const minute = now.getMinutes();
        const second = now.getSeconds();
        const day = now.getDate();
        const month = now.getMonth() + 1;
        const year = now.getFullYear();

        // Form texts
        const time_text = (hour < 10 ? "0" + hour : hour) + ':' + (minute < 10 ? "0" + minute : minute) + ':' + (second < 10 ? "0" + second : second);
        const date_text = (day < 10 ? "0" + day : day) + '.' + (month < 10 ? "0" + month : month) + '.' + year;

        // Write HTML
        this.time_obj.html(time_text);
        this.date_obj.html(date_text);
        this.init_timer();
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
