'use strict';

var generators = require('yeoman-generator');
var user = require('../node_modules/yeoman-generator/lib/actions/user');

var config = {};

module.exports = generators.Base.extend({
  prompting: function(){
    var done = this.async();
    this.prompt({
      type    : 'input',
      name    : 'name',
      message : 'Your project name',
      default : this.config.get('name') // value set in .yo-rc.json
    }, function (answers) {
      // TODO check if this view already exist
      config.name = answers.name;
      done();
    }.bind(this));
  },
  writing: {
    rcFiles: function(){
      this.fs.copy(this.templatePath('.bowerrc'), this.destinationPath(`${this.config.get('folder')}/${config.name}/.bowerrc`));
      this.fs.copy(this.templatePath('.gitignore'), this.destinationPath(`${this.config.get('folder')}/${config.name}/.gitignore`));
    },
    packageJson: function(){
      this.fs.copyTpl(
        this.templatePath('package.json'),
        this.destinationPath(`${this.config.get('folder')}/${config.name}/package.json`),
        { name: config.name, author: {name:user.git.name()} }
      );
    },
    bowerJson: function(){
      this.fs.copyTpl(
        this.templatePath('bower.json'),
        this.destinationPath(`${this.config.get('folder')}/${config.name}/bower.json`),
        { name: config.name, author: {name:user.git.name(), email: user.git.email()} }
      );
    },
    index: function(){
      this.fs.copyTpl(
        this.templatePath('src/index.html'),
        this.destinationPath(`${this.config.get('folder')}/${config.name}/src/index.html`),
        { name: config.name }
      );
    },
    mainJs: function(){
      this.fs.copyTpl(
        this.templatePath('src/js/main.js'),
        this.destinationPath(`${this.config.get('folder')}/${config.name}/src/js/main.js`),
        { name: config.name }
      );
    },
    template: function(){
      this.fs.copy(this.templatePath('src/templates/users-list.tpl.html'), this.destinationPath(`${this.config.get('folder')}/${config.name}/src/templates/users-list.tpl.html`));
    },
    gulp: function(){
      this.fs.copy(this.templatePath('gulp/*.js'), this.destinationPath(`${this.config.get('folder')}/${config.name}/gulp`));
      this.fs.copy(this.templatePath('gulpfile.js'), this.destinationPath(`${this.config.get('folder')}/${config.name}/gulpfile.js`));
    }
  },
  install: function(){
    var done = this.async();
    this.prompt({
      type    : 'confirm',
      name    : 'deps',
      message : 'Install dependecies?',
      default : false // value set in .yo-rc.json
    }, function (answers) {
      if(answers.deps){
        process.chdir(`${this.config.get('folder')}/${config.name}`);
        this.installDependencies();
      }
      done();
    }.bind(this));
  }
});
