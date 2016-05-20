# ngXosLib

This is a collection of helpers to develop views as Angular SPA.

## Tools

This tools are designed to help you developing UI for XOS. As they born for this purpose if often necessary that a XOS instance is running on your sistem and responding at: `localhost:9999`. The `xos/configurations/frontend` is normally enough.

### Vendors

Xos comes with a preset of common libraries, as listed in `bower.json`:
- angular
- angular-route
- angular-resource
- angular-cookie
- angular-animate
- ng-lodash

This libraries are served through Django, so they will not be included in your minified vendor file. To add a library and generate a new file (that will override the old one), you should:
- enter `ngXosLib` folder
- run `bower install [myPackage] --save`
- rebuild the file with `gulp vendor`

>_NOTE before adding libraries please discuss it to avoid this file to became huge_

### Helpers

XOS comes with an helper library that is automatically loaded in the Django template. It a set of Services and UI Components

To use it, add `xos.helpers` to your required modules:

```
angular.module('xos.myView', [
  'xos.helpers'
])
```

It will automatically ad a `token` to all your request, eventually you can take advantage of some other services:

To develop components inside this folder there is a particular command: `npm run dev`, this will watch the helpers file and rebuild them with sourcemaps. For this reason remember to build them when done developing.

>While developing components in this library you should execute the test. The `npm test` command will run Jasmine test for the whole complete library.
>If you want to specify a single test file to be execute, you can add it to the command like: `npm test smart-pie`, the tool will now read only the test specified in the `smart-pie.test.js` file.

When some changes are applied to this common library it should be rebuilt with: `npm run build`

To generate the relative documentation use: `npm run doc`

### Yo Xos

We have created a [yeoman](http://yeoman.io/) generator to help you scaffolding views.

>As it is in an early stage of development you should manually link it to your system, to do this enter `xos/views/ngXosLib/generator-xos` and run `npm install && npm link`.

#### To generate a new view

From `xos/views` run `yo xos`. This command will create a new folder with the provided name in: `xos/views/ngXosViews` that contain your application.

>If you left empty the view name it should be `xos/views/ngXosViews/sampleView`

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

The `npm start` command is watching your dependencies and will automatically inject them in your `index.html`.

#### Linting

A styleguide is enforced trough [EsLint](http://eslint.org/) and is checked during the build process. We **highly** suggest to install the linter in your editor to have realtime hint.

#### Test

The generator set up a test environment with a default test.
To run it execute: `npm test`

## TODO

- Define styleguide (both visual and js) and if needed define some UI components