# ngXosLib

This is a collection of helpers to develop views as Angular SPA.

## Tools

### Apigen

Usage: `npm run apigen`

This tool will automatically generate an angular resource file for each endpoint available in Swagger. 

_NOTE: endpoints are listed as an array `apiList` in `xos-resource-generator.js`. If a new endpoint is added, it should be added also to that list._

## TODO

- Use Angular $resource instead of $http
- Use ngDoc instead of jsDoc
- Yeoman generator for new view
- Define styleguide (both visual and js) and if needed define some UI components