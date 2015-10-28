# XOS Lib Helper

This library should help you while developing with:

#### Serve
- Install Bower deps
- Load js files (from args folder)
- Load html templates (from args folder)
- Compile ES6
- Compile Scss
- Compile template using `ng2html`
- Watch source folder
- Livereload
- Generate a basic index.html in a `dist` folder under `args` folder loading files

#### Build
- Install Bower deps
- Load js files (from args folder)
- Load html templates (from args folder)
- Compile ES6
- Compile Scss
- Compile template using `ng2html`
- Minify Js & Css
- Prefix Css
- Cicle trough `bower.json` and diff it with base `bower.json` to exclude already loaded modules (eg: angular) [Optional]
- Move `dist` under xos folder

## App Structure

App Name
└- src
   ├ js
   ├ templates
   ├ bower_components
   └ dist

Angular apps should be saved under `xoslib/source` and builded apps should be moved under `xoslib/static/js`. 

Two files should be generated, `appname_main.js` and `appname_vendor.js`, these file should be included into `xoslib/dashboards/appname.html` (tbd if this file has to be automatically generated during the build)

## Advantages

- Faster development with common tool
- Standard build for community developer
- Minified files

