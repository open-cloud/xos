# ngXosLib

This is a collection of helpers to develop views as Angular SPA.

## Tools

These tools are designed to help develop a graphical view. They assume XOS is running on your system and responding at: `localhost:9999`. The `xos/configurations/frontend` is normally sufficient for GUI development.

### Vendors

XOS comes with a set of common libraries, as listed in `bower.json`:
- angular
- angular-route
- angular-resource
- angular-cookie
- ng-lodash

These libraries are served through Django, so they are not included in your minified vendor file. To add a library and generate a new file (that will override the old one):
- enter `ngXosLib` folder
- run `bower install [myPackage] --save`
- rebuild the file with `gulp vendor`

>_NOTE before adding libraries please discuss it on the devel list to avoid this file becoming too big_

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

>_NOTE: for the API related service, check the documentation in Section [Apigen](#apigen)._

# ngXosViews

In addition to auto-generated Django Admin Views and developer-defined Service Views, a set of custom views can be generate in XOS.

These views are based on AngularJs and they communicate with XOS through the REST APIs, providing a powerful and flexible way to present and manage data.

## How to Create a View

### Environment setup

Before getting started with new views you should create a configuration file to define the backend environment to be used. This file have to be in `views/env/default.js` and it content have to be:

```
module.exports = {
  host: 'XOS Url',
  xoscsrftoken: 'CSRF Token',
  xossessionid: 'Sessio ID'
};
```

You can define multiple environment creating other configurations (eg: `views/env/production.js`) with the same structure.

### Getting Started

We have created a [yeoman](http://yeoman.io/) generator to help scaffold views.

>As it is in an early stage of development, you should manually link it to your system. To do this enter `/views/ngXosLib/generator-xos` and run `npm link`.

#### To Generate a New View

From `/views` run `yo xos`. This command will create a new folder with the provided name in `/views/ngXosViews` that contains your application.

>If you left View name empty it should be `/views/ngXosViews/sampleView`

#### Run a Development Server

In your `view` folder run `npm start`.

This will install the required dependencies and start a local server with [BrowserSync](http://www.browsersync.io/).

>If you want to use a different backend environment you can call the command with an environment variable: `NODE_ENV=production.js npm start`

#### Publish Your View

Once your view is done, from your view root folder, run: `npm run build`.

This will build your application and copy files in the appropriate directories for use by Django.

At this point you can enter: `http://localhost:9999/admin/core/dashboardview/add/` and add your custom view.

>_NOTE: url field should be `template:xosSampleView`_

##### Add This View to a Configuration Setup

You can easily set this as a default view in a configuration by editing the `{config}.yml` file for that configuration. Add these lines:

```
{TabName}:                                    
  type: tosca.nodes.DashboardView              
  properties:                                  
      url: template:{viewName}     
```

Then edit the _User_ section (normally it starts with `padmin@vicci.org`) as follows:

```
padmin@vicci.org:                                          
  type: tosca.nodes.User                                   
  properties:                                              
      firstname: XOS                                       
      lastname: admin                                      
      is_admin: true                                       
  requirements:                                            
      - tenant_dashboard:                                  
          node: Tenant                                     
          relationship: tosca.relationships.UsesDashboard  
      - {custom_dashboard}:                              
          node: {TabName}                                 
          relationship: tosca.relationships.UsesDashboard  
```

#### Install Dependencies in Your App

To install a local dependency use bower with `--save`. Common modules are saved in `devDependencies` as they already loaded in the Django template.

The `npm start` command watches your dependencies and will automatically inject it in your `index.html`.

#### Linting

A styleguide is enforced through [EsLint](http://eslint.org/) and is checked during the build process. We **highly** recommend installing the linter in your editor to have realtime hints.

#### Test

The generator sets up a test environment with a default test.
To run it, execute: `npm test`

