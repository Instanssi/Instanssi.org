'use strict';

var webpack = require('webpack');

// webpack configuration
module.exports = {
    // where to start
    entry: {
        '../backend/Instanssi/store/static/store/js/bundle.js': './js/index.js'
    },
    // what to output
    output: {
        // [name] is the name of the entry point, so this names output bundles
        // like './store/static/store/js/bundle.js'
        filename: '[name]'
    },
    // how to import things
    module: {
        // import handling rules
        rules: [
            {
                // import .js files by running them through babel (to handle ES2015 syntax)
                // webpack can then bundle the results
                test: /\.js$/,
                // babel should find our .babelrc and get dialect settings from there
                use: ['babel-loader']
            },
            {
                test: /\.html$/,
                use: [{
                    loader: 'html-loader',
                    options: {
                        minimize: true,
                        // Vue templates are not _exactly_ HTML
                        caseSensitive: true,
                    }
                }]
            }
        ]
    },
    // map import names to globals in browser environment
    // this allows strict namespacing while accessing external JS
    externals: {
        // importing 'vue' returns value of global 'Vue'
        vue: 'Vue'
    },
    // additional plugins
    plugins: [
        new webpack.optimize.UglifyJsPlugin(),
        new webpack.optimize.ModuleConcatenationPlugin(),
    ]
};
