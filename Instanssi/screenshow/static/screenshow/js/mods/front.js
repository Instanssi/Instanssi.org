"use strict";

/*
 * Screenshow Frontpage module
 * Author: Tuomas Virtanen
 */

function ScreenFrontpage(settings, jmobj, obj) {
    this.settings = settings; 
    this.jmobj = jmobj;
    this.obj = obj;

    this.init = function() { this.obj.html('Instanssi'); }
    this.post_init = function() {}
    this.update = function() {}
}
