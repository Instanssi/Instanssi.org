"use strict";

/*
 * Screenshow Frontpage module
 * Author: Tuomas Virtanen
 */

function ScreenFrontpage(jmobj, obj) {
    this.jmobj = jmobj;
    this.obj = obj;

    this.getObj = function() { return this.obj; }
    this.init = function() { this.obj.html("Instanssi"); }
    this.update = function() {}
}
