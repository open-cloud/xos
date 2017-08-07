
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


(function () {
  angular.module('xos.UITutorial')
  .service('codeToString', function(){
    this.toString = code => {
      if(angular.isArray(code)){
        return code.map(item => this.toString(item));
      }
      else if(angular.isObject(code)){
        let tmp = {};
        Object.keys(code).forEach(key => {
          tmp[key] = this.toString(code[key])
        });
        return tmp;
      }
      else{
        return code.toString().split('\n').join('').replace(/ +(?= )/gmi, '');
      }
    };

    this.toCode = string => {
      let code;

      try {
        code = JSON.parse(string);
      }
      catch(e){
        code = string;
      }
      
      if(angular.isArray(code)){
        return code.map(item => this.toCode(item));
      }
      else if(angular.isObject(code)){
        let tmp = {};
        Object.keys(code).forEach(key => {
          tmp[key] = this.toCode(code[key])
        });
        return tmp;
      }
      else{
        if(!angular.isNumber(code) && code.indexOf('function') !== -1){
          try {
            return function(){
              // create a closure to host our arguments
              var func = new Function(`return ${code}`);
              
              // invoke the original function passing arguments
              func()(...arguments);
            }
          }
          catch(e){
            // in this case it is a string
            return code;
          }
        }
        else if(Number.isNaN(code)){
          return parseFloat(code);
        }
        return code;
      }

      return code;
    };
  });
})();