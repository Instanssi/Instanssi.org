'use strict';

module.exports = {
    process: function(src, _path) {
        return 'module.exports = ' + JSON.stringify(src) + ';';
    }
};
