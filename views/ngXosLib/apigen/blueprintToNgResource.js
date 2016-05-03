'use strict';

const protagonist = require('protagonist');
const fs = require('fs');
const P = require('bluebird');
const _ = require('lodash');
const chalk = require('chalk');
const Handlebars = require('handlebars');
const util = require('util');
const path = require('path');

P.promisifyAll(fs);
P.promisifyAll(protagonist);

const angualarModuleName = 'xos.helpers'

const findCommonString = (array) => {
  let A = array.concat().sort();
  let a1 = A[0];
  let a2= A[A.length-1];
  let L= a1.length;
  let i= 0;
  while(i<L && a1.charAt(i)=== a2.charAt(i)) i++;
  return a1.substring(0, i);
};

// format href in angular format
const formatHref = url => url.replace(/({\?.+})/, '').replace('{', ':').replace('}', '');

const formatTitle = title => title.split(' ').join('-');

const getParamName = url => url.match(/:([a-z]+)\/*/) ? url.match(/:([a-z]+)\/*/)[1] : '';

// Get Group description
const getGroupDescription = (group) => _.find(group, {element: 'copy'}) ? _.find(group, {element: 'copy'}).content.replace(/\n$/, '') : '';

// get the base url for a group
const getBaseUrl = (group) => {

  // TODO make param name dynamic

  let urls = group.reduce((list, g) => list.concat(g.param.href), []);
  
  let baseUrl = findCommonString(urls)

  let baseUrlWithId;

  if(baseUrl.indexOf(':id') >= 0){
    baseUrlWithId = _.indexOf(urls, `${baseUrl}`);
  }
  else{
    baseUrlWithId = _.indexOf(urls, `${baseUrl}:id/`);
  }

  return {
    href: baseUrlWithId >= 0 ? urls[baseUrlWithId] : baseUrl,
    param: baseUrlWithId >= 0 ? 'id' : ''
  }
};

// Loop APIs endpoint
const loopApiEndpoint = (group) => {
  // console.log(group);
  // removing description
  _.remove(group, {element: 'copy'})

  return _.map(group, g => {
    let url = formatHref(g.attributes.href);
    return {
      name: formatTitle(g.meta.title),
      param: {href: url, name: getParamName(url)},
    }
  })
};


// list all the requested defined in a group,
// return {method, url, isArray}
const getGroupMethods = (group, baseUrl) => {

  _.remove(group, {element: 'copy'})

  let actions = [];

  _.forEach(group, g => {
    _.remove(g.content, {element: 'copy'})
    // console.log('-----------------------');
    // console.log(g);
    let url = formatHref(g.attributes.href);
    _.forEach(g.content, action => {
      // if it is a base method (Query, Save, $save, $delete, $update) return
      if(baseUrl.indexOf(url) >= 0){
        // console.info('base method');
        return
      }
      // console.log(baseUrl, url);

      // console.log(action);
      let name = action.meta.title;
      let method = action.content[0].content[0].attributes.method;
      let response = _.find(action.content[0].content, {element: 'httpResponse'}).content[0] ? _.find(action.content[0].content, {element: 'httpResponse'}).content[0].content : null;
      let isArray = Array.isArray(JSON.parse(response));
      // console.log(method, url, isArray, name);


      actions.push({
        method: method,
        url: url,
        isArray: isArray,
        name: formatTitle(name)
      })
    })
  });

  return actions;
}

// Loop APIs groups
const loopApiGroups = (defs) => {

  let formattedData = {};

  // console.log(util.inspect(defs, false, null));

  if (!Array.isArray(defs)) {
    return;
  }
  _.forEach(defs, d => {
    if(process.env.NODE_ENV !== 'test'){
      console.info(chalk.blue.bold(`Parsing Group: ${d.meta.title}`));
    }

    let endpoints = loopApiEndpoint(d.content);
    let baseUrl = getBaseUrl(endpoints);

    let data = {
      description: getGroupDescription(d.content),
      baseUrl: baseUrl,
      resourceName: d.meta.title,
      ngModule: angualarModuleName,
      customActions: getGroupMethods(d.content, baseUrl.href)
    };

    if(process.env.NODE_ENV !== 'test'){
      fs.writeFileSync(path.join(__dirname, `../xosHelpers/src/services/rest/${formatTitle(d.meta.title)}.js`), handlebarsTemplate(data));
    }

    formattedData[d.meta.title] = data;
  });

  if(process.env.NODE_ENV !== 'test'){
    console.info(chalk.green.bold(`Api Generated`));
  }
  return formattedData;
};

// Loop the top level definitions
const loopApiDefinitions = (defs) => {
  // console.log(util.inspect(defs, false, null));
  _.forEach(defs, d => loopApiGroups(d.content));
};

let handlebarsTemplate;

// read blueprint docs and parse
fs.readFileAsync(path.join(__dirname, './ngResourceTemplate.handlebars'), 'utf8')
.then((template) => {
  handlebarsTemplate = Handlebars.compile(template);
  // return fs.readFileAsync(path.join(__dirname, '../../../apiary.apib'), 'utf8')
  // return fs.readFileAsync(path.join(__dirname, '../../../xos/tests/api/source/tenant/cord/subscribers.md'), 'utf8')
  // return fs.readFileAsync(path.join(__dirname, '../../../xos/tests/api/source/core/instances.md'), 'utf8')
  // return fs.readFileAsync(path.join(__dirname, '../../../xos/tests/api/source/core/deployment.md'), 'utf8')
  return fs.readFileAsync(path.join(__dirname, '../../../xos/tests/api/source/utility/utility.md'), 'utf8')
})
.then(data => protagonist.parseAsync(data))
.then(result => loopApiDefinitions(result.content))
.catch(console.warn);

exports.findCommonString = findCommonString;
exports.formatHref = formatHref;
exports.getParamName = getParamName;
exports.getBaseUrl = getBaseUrl;
exports.loopApiEndpoint = loopApiEndpoint;
exports.getGroupMethods = getGroupMethods;
exports.loopApiGroups = loopApiGroups;

