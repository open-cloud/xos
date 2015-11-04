# ngXosLib

This is a collection of helpers to develop views as Angular SPA.

## Tools

This tools are designed to help you developing UI for XOS. As they born for this purpose if often necessary that a XOS instance is running on your sistem and responding at: `localhost:9999`. The `xos/configurations/frontend` is normally enough.

### Apigen

Usage: `npm run apigen`

This tool will automatically generate an angular resource file for each endpoint available in Swagger. 

_NOTE: endpoints are listed as an array `apiList` in `xos-resource-generator.js`. If a new endpoint is added, it should be added also to that list._

### Vendors

Xos comes with a preset of common libraries, as listed in `bower.json`:
- angular
- angular-route
- angular-resource
- angular-cookie
- ng-lodash

This libraries are server through Django, so they will not be included in your minified vendor file. To add a library and generate a new file (that will override the old one), you should:
- enter `ngXosLib` folder
- run `bower install [myPackage] --save`
- rebuild the file with `gulp vendor`

>_NOTE before adding libraries please discuss it to avoid this file to became huge_

### Helpers

XOS comes with an helper library that is automatically loaded in the Django template.

To use it, add `xos.helpers` to your required modules:

```
angular.module('xos.myView', [
  'xos.helpers'
])
```

It will automatically ad a `token` to all your request, eventually you can take advantage of some other services:

- **NoHyperlinks Interceptor**: will add a `?no_hyperlinks=1` to your request, to tell Django to return ids instead of links.

### Yo Xos

We have created a [yeoman](http://yeoman.io/) generator to help you scaffolding views.

>As it is in an early stage of development you should manually link it to your system, to do this enter `xos/core/xoslib/ngXosLib/generator-xos` and run `npm link`.

#### To generate a new view

From `xos/core/xoslib` run `yo xos`. This command will create a new folder with the provided name in: `xos/core/xoslib/ngXosViews` that contain your application.

>If you left empty the view name it should be `xos/core/xoslib/ngXosViews/sampleView`

#### Run a development server

In your `view` folder and run `npm start`.

_This will install required dependencies and start a local server with [BrowserSync](http://www.browsersync.io/)_

#### Publish your view

Once your view is done, from your view root folder, run: `npm run build`.

This will build your application and copy files in the appropriate locations to be used by django.

At this point you can enter: `http://localhost:9999/admin/core/dashboardview/add/` and add your custom view.

>_NOTE url field should be `template:xosSampleView`_

#### Install dependencies in your app

To install a local dependency use bower with `--save`. Common modules are saved in `devDependencies` as they already loaded in the Django template.

The `npm start` command is watching your dependencies and will automatically inject it in your `index.html`.

#### Test

The generator set up a test environment with a default test.
To run it execute: `npm test`

## TODO

- Use Angular $resource instead of $http
- Use ngDoc instead of jsDoc
- Define styleguide (both visual and js) and if needed define some UI components
- Load api endpoints from `http://localhost:9999/docs/api-docs/`