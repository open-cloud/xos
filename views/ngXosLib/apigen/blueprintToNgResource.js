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

// format href in angular format
const formatHref = url => url.replace('{', ':').replace('}', '');

const formatTitle = title => title.split(' ').join('-');

const getParamName = url => url.match(/\{([^)]+)\}/) ? url.match(/\{([^)]+)\}/)[1] : '';

// Get Group description
const getGroupDescription = (group) => _.find(group, {element: 'copy'}) ? _.find(group, {element: 'copy'}).content.replace(/\n$/, '') : '';

// Loop APIs endpoint
const loopApiEndpoint = (group) => {
  // {name: 'ResourceName', attributes: {href: '/ahhsiiis'}}
  _.remove(group, {element: 'copy'})
  // console.log(group);
  // _.forEach(group, d => console.log(d));

  return _.map(group, g => {
    return {
      name: formatTitle(g.meta.title),
      param: {href: formatHref(g.attributes.href), name: getParamName(g.attributes.href)},
    }
  })
};

// Loop APIs groups
const loopApiGroups = (defs) => {
  if (!Array.isArray(defs)) {
    return;
  }
  _.forEach(defs, d => {
    console.info(chalk.blue.bold(`Parsing Group: ${d.meta.title}`));
    var data = {
      description: getGroupDescription(d.content),
      ngModule: angualarModuleName,
      resources: loopApiEndpoint(d.content)
    };
    fs.writeFileSync(path.join(__dirname, `../xosHelpers/src/services/rest/${formatTitle(d.meta.title)}.js`), handlebarsTemplate(data));
  });

  console.info(chalk.green.bold(`Api Generated`));

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
  return fs.readFileAsync(path.join(__dirname, '../../../apiary.apib'), 'utf8')
})
.then(data => protagonist.parseAsync(data))
.then(result => loopApiDefinitions(result.content))
.catch(console.warn);

