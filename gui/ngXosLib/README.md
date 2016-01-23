# ngXosLib

A collection of programs to develop Views as Angular SPA.

## Tools

These tools are designed to help develop UIs for XOS. They assume XOS is running on your system at `localhost:9999`. The `xos/configurations/frontend` is normally a sufficient configuration for development.

### Apigen

Usage: `npm run apigen`

This tool generates an angular resource file for each endpoint available in Swagger.

>You can generate api related documentation with: `npm run apidoc`. The output is locate in `api/docs`. You can also see a list of available methods through Swagger at `http://localhost:9999/docs/`

### Vendors

XOS comes with a set of common libraries, as listed in `bower.json`:
- angular
- angular-route
- angular-resource
- angular-cookie
- ng-lodash

These libraries are served through Django, so they will not be included in your minified vendor file. To add a library and generate a new file (that will override the old one):
- enter `ngXosLib` folder
- run `bower install [myPackage] --save`
- rebuild the file with `gulp vendor`

>_NOTE: before adding libraries please discuss it on the devel list to avoid this file becoming huge_

### Helpers

XOS comes with a helper library that is automatically loaded in the Django template.

To use it, add `xos.helpers` to your required modules:

```
angular.module('xos.myView', [
  'xos.helpers'
])
```

It will automatically add a `token` to all your requests. Eventually you can take advantage of some other services:

- **NoHyperlinks Interceptor**: will add a `?no_hyperlinks=1` to your request, to tell Django to return ids instead of links.
- **XosApi** wrapper for `/xos` endpoints.
- **XoslibApi** wrapper for `/xoslib` endpoints.
- **HpcApi** wrapper for `/hpcapi` endpoints.

>_NOTE: for the API related service, check documentation in [Apigen](#apigen) section._

### Yo XOS

We have created a [yeoman](http://yeoman.io/) generator to help to scaffold views.

>As it is in an early stage of development you should manually link it to your system. To do this, enter `xos/core/xoslib/ngXosLib/generator-xos` and run `npm link`.

#### To Generate a New View

From `xos/core/xoslib` run `yo xos`. This command creates a new folder with the provided name in: `xos/core/xoslib/ngXosViews` that contain your application.

>If you left the View name empty, it should be `xos/core/xoslib/ngXosViews/sampleView`

#### Run a Development Server

In your `view` folder run `npm start`.

_This will install the required dependencies and start a local server with [BrowserSync](http://www.browsersync.io/)_

#### Publish your View

Once your view is done, from your view root folder, run: `npm run build`.

This will build your application and copy files in the appropriate locations to be used by Django.

At this point you can enter: `http://localhost:9999/admin/core/dashboardview/add/` and add your custom view.

>_NOTE url field should be `template:xosSampleView`_

#### Install Dependencies in Your app

To install a local dependency, use bower with `--save`. Common modules are saved in `devDependencies` as they already loaded in the Django template.

The `npm start` command watches your dependencies and automatically injects it in your `index.html`.

#### Linting

A styleguide is enforced through [EsLint](http://eslint.org/) and is checked during the build process. We **highly** suggest installing the linter in your editor to have realtime hints.

#### Test

The generator sets up a test environment with a default test.
To run it execute: `npm test`

## TODO

- Use Angular $resource instead of $http
- Use ngDoc instead of jsDoc
- Define styleguide (both visual and js) and if needed define some UI components
