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