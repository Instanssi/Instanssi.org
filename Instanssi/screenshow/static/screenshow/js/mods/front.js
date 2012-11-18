"use strict";

/*
 * Screenshow Frontpage module
 * Author: Tuomas Virtanen
 */

function ScreenFrontpage(jmobj, obj) {
    this.jmobj = jmobj;
    this.obj = obj;

    this.init = function() { this.obj.html("Instanssi"); }
    this.post_init = function() {}
    this.update = function() {}
}
