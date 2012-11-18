"use strict";

/*
 * Example module
 * Author: Tuomas Virtanen
 */

function ScreenExample(jmobj, obj) {
    this.jmobj = jmobj; // This is the jmpress element
    this.obj = obj; // This is the element owned by the module

    /**
     * Init function is a good place for writing HTML and initializing 
     * external libraries. 
     */
    this.init = function() { this.obj.html("Instanssi"); }
    
    /**
     * Everything related to jmpress initialization should be done here.
     * eg. attaching event listeners, changing data, etc. 
     */
    this.post_init = function() {}
    
    /**
     * This will be called when the "frontpage" slide is hit.
     * Data acquisition & updates & slide content changes should be handled here. 
     */
    this.update = function() {}
}
