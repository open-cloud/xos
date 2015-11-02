#! /usr/bin/env node
'use strict';

const assert = require('assert');
const chalk = require('chalk');

const args = process.argv.slice(2);

const error = chalk.white.bgRed;
const success = chalk.white.bgGreen;

const task = args[0];
if(!task){
  console.log(error('A task should be defined'))
  process.exit(1);
}

console.log(success('Build Started for'));

console.log(process.argv);
