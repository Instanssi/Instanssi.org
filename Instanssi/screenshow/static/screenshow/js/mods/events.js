"use strict";

/*
 * Screenshow Events module
 * Author: Tuomas Virtanen
 */

function ScreenEvents(settings, jmobj, obj, url) {
    this.settings = settings; 
    this.obj = obj;
    this.url = url;
    this.jmobj = jmobj;
    this.timeout = 3000;
    
    this.init = function() {}
    this.post_init = function() {}
    
    this.fetch_success = function(data) {
        // Fetch and render data
        var output = '<table>';
        $.each(data['events'], function(key, value) {
            output += '<tr><td>';
            output += value['date'];
            output += '</td><td>&raquo;</td><td>';
            output += value['title'];
            output += '</td></tr>';
        });
        output += '</table>';
        this.obj.html(output);
        
        // Show only if there is data to show :)
        this.obj.data("stepData").exclude = (output.length === 0);
        this.jmobj.jmpress('reapply', this.obj);
    }
    
    this.fetch_error = function(jqXHR, status, errorThrown) {
        console.log("There was a problem while fetching event data.");
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
