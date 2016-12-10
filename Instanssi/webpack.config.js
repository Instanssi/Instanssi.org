var webpack = require('webpack');

// modules that need a JS bundle
var modules = [
    'store'
];

var entryPoints = {};
modules.forEach(function(name) {
    // generate entry point mappings like
    // 'store/static/store/js/index.js': './store/static/store/js/src/index.js'
    entryPoints[name + '/static/' + name + '/js/index.js'] = './' + name + '/static/' + name + '/js/src/index.js';
})

// webpack configuration
module.exports = {
  // where to start
  entry: entryPoints,
  // what to output
  output: {
    // [name] is the name of the entry point, so this names output bundles like './store/static/store/js/index.js'
    filename: '[name]'
  },
  // how to import things
  module: {
    // import handling rules
    rules: [{
      // import js files by running them through babel (to handle ES2015 syntax)
      // webpack can then bundle the results 
      test: /\.js$/,
      // babel should find our .babelrc and get dialect settings from there 
      loader: 'babel-loader',
      options: {
        presets: [ 'babel-preset-es2015' ]
      }
    }]
  },
  // map import names to globals in browser environment
  // this allows strict namespacing while accessing external JS
  externals: {
    // importing 'vue' returns value of global 'Vue'
    vue: 'Vue'
  },
  // additional plugins
  plugins: [
    new webpack.optimize.UglifyJsPlugin()
  ]
}
