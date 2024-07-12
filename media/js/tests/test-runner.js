/* eslint-env node */
var process = require('process');

var requirejs = require('requirejs');
requirejs.config({
    paths: {
        'jquery': '../lib/jquery-3.3.1.min',
        'domReady': '../lib/require/domReady',
        'underscore': '../lib/underscore-min'
    },
    //Pass the top-level main.js/index.js require
    //function to requirejs so that node modules
    //are loaded relative to the top-level JS file.
    nodeRequire: require
});

var Mocha = require('mocha');
var fs = require('fs');
var path = require('path');

var basePath = './media/js/tests';
var mocha = new Mocha();


fs.readdirSync(basePath).filter(function(file) {
    // eslint-disable-next-line no-undef
    return file !== __filename && file.substr(-3) === '.js';
}).forEach(function(file) {
    mocha.addFile(path.join(basePath, file));
});

mocha.run(function(failures) {
    process.on('exit', function() {
        process.exit(failures);
    });
});
