// TryMongo
//
// Copyright (c) 2009 Kyle Banker
// Licensed under the MIT Licence.
// http://www.opensource.org/licenses/mit-license.php

// Readline class to handle line input.
var ReadLine = function(options) {
  this.options      = options || {};
  this.htmlForInput = this.options.htmlForInput;
  this.inputHandler = this.options.handler || this.mockHandler;
  this.scoper       = this.options.scoper;
  this.terminal     = $(this.options.terminalId || "#terminal");
  this.lineClass    = this.options.lineClass || '.readLine';
  this.history      = [];
  this.historyPtr   = 0;

  this.initialize();
};

ReadLine.prototype = {

  initialize: function() {
    this.addInputLine();
  },

  // Enter a new input line with proper behavior.
  addInputLine: function(stackLevel) {
    stackLevel = stackLevel || 0;
    this.terminal.append(this.htmlForInput(stackLevel));
    var ctx = this;
    ctx.activeLine = $(this.lineClass + '.active');

    // Bind key events for entering and navigting history.
    ctx.activeLine.bind("keydown", function(ev) {
      switch (ev.keyCode) {
        case EnterKeyCode:
          ctx.processInput(this.value); 
          break;
        case UpArrowKeyCode: 
          ctx.getCommand('previous');
          break;
        case DownArrowKeyCode: 
          ctx.getCommand('next');
          break;
      }
    });

    this.activeLine.focus();
  },

  // Returns the 'next' or 'previous' command in this history.
  getCommand: function(direction) {
    if(this.history.length === 0) {
      return;
    }
    this.adjustHistoryPointer(direction);
    this.activeLine[0].value = this.history[this.historyPtr];
    $(this.activeLine[0]).focus();
    //this.activeLine[0].value = this.activeLine[0].value;
  },

  // Moves the history pointer to the 'next' or 'previous' position. 
  adjustHistoryPointer: function(direction) {
    if(direction == 'previous') {
      if(this.historyPtr - 1 >= 0) {
        this.historyPtr -= 1;
      }
    }
    else {
      if(this.historyPtr + 1 < this.history.length) {
        this.historyPtr += 1;
      }
    }
  },

  // Return the handler's response.
  processInput: function(value) {
    var response = this.inputHandler.apply(this.scoper, [value]);
    this.insertResponse(response.result);

    // Save to the command history...
    if((lineValue = value.trim()) !== "") {
      this.history.push(lineValue);
      this.historyPtr = this.history.length;
    }

    // deactivate the line...
    this.activeLine.value = "";
    this.activeLine.attr({disabled: true});
    this.activeLine.removeClass('active');

    // and add add a new command line.
    this.addInputLine(response.stack);
  },

  insertResponse: function(response) {
    if((response.length < 1) || (response=='"donotprintme"') || (response=='donotprintme')) {
      this.activeLine.parent().append("<p class='response'></p>");
    }
    else {
      this.activeLine.parent().append("<p class='response'>" + response + "</p>");
    }
  },

  // Simply return the entered string if the user hasn't specified a smarter handler.
  mockHandler: function(inputString) {
    return function() {
      this._process = function() { return inputString; };
    };
  }
};

var MongoHandler = function() {
  this._currentCommand = "";
  this._rawCommand     = "";
  this._commandStack   = 0;
  this._tutorialPtr    = 0;
  this._tutorialMax    = 4;

  this._mongo          = {};
  this._mongo.test     = [];
  this.collections     = [];
};

MongoHandler.prototype = {

  _process: function(inputString, errorCheck) {
    this._rawCommand += ' ' + inputString;

    try {
      inputString += '  '; // fixes certain bugs with the tokenizer.
      var tokens    = inputString.tokens();
      var mongoFunc = this._getCommand(tokens);
      if(this._commandStack === 0 && inputString.match(/^\s*$/)) {
        return {stack: 0, result: ''};
      }
      else if(this._commandStack === 0 && mongoFunc) {
        this._resetCurrentCommand();
        return {stack: 0, result: mongoFunc.apply(this, [tokens])};
      }
      else {
        return this._evaluator(tokens);
      }
    }

    catch(err) {
        this._resetCurrentCommand();
        console.trace();
        return {stack: 0, result: "JS Error: " + err};
    }
  },

  // Calls eval on the input string when ready.
  _evaluator: function(tokens) {
    isAssignment = tokens.length>=2 && tokens[0].type=="name" && tokens[1].type=="operator" && tokens[1].value=="=";

    this._currentCommand += " " + this._massageTokens(tokens);
    if(this._shouldEvaluateCommand(tokens))  {
        print = this.print;

        // So this eval statement is the heart of the REPL.
        var result = eval(this._currentCommand.trim());
        if(result === undefined) {
          throw('result is undefined');
        } else if (typeof(result) === 'function') {
          throw('result is a function. did you mean to call it?');
        } else {
          result = $htmlFormat(result);
        }
        this._resetCurrentCommand();
        if (isAssignment) {
            return {stack: this._commandStack, result: ""};
        } else {
            return {stack: this._commandStack, result: result};
        }
      }

    else {
      return {stack: this._commandStack, result: ""};
    }
  },

  _resetCurrentCommand: function() {
    this._currentCommand = '';
    this._rawCommand     = '';
  },

  // Evaluate only when we've exited any blocks.
  _shouldEvaluateCommand: function(tokens) {
    for(var i=0; i < tokens.length; i++) {
      var token = tokens[i];
      if(token.type == 'operator') {
        if(token.value == '(' || token.value == '{') {
          this._commandStack += 1;
        }
        else if(token.value == ')' || token.value == '}') {
          this._commandStack -= 1;
        }
      }
    }

    if(this._commandStack === 0) {
      return true;
    }
    else {
      return false;
    }
  },

  _massageTokens: function(tokens) {
    for(var i=0; i < tokens.length; i++) {
      if(tokens[i].type == 'name') {
        if(tokens[i].value == 'var') {
          tokens[i].value = '';
        }
      }
    }
    return this._collectTokens(tokens);
  },

  // Collects tokens into a string, placing spaces between variables.
  // This methods is called after we scope the vars.
  _collectTokens: function(tokens) {
    var result = "";
    for(var i=0; i < tokens.length; i++) {
      if(tokens[i].type == "name" && tokens[i+1] && tokens[i+1].type == 'name') {
        result += tokens[i].value + ' ';
      }
      else if (tokens[i].type == 'string') {
        result += "'" + tokens[i].value + "'";
      }
      else {
        result += tokens[i].value;
      }
    }
    return result;
  },

  // print output to the screen, e.g., in a loop
  // TODO: remove dependency here
  print: function() {
   $('.readLine.active').parent().append('<p>' + JSON.stringify(arguments[0]) + '</p>');
   return "donotprintme";
  },

  /* MongoDB     */
  /* ________________________________________ */

  // help command
  _help: function() {
      return PTAG('HELP') +
             PTAG('xos                                 list xos API object types') +
             PTAG('xos.slices.fetch()                  fetch slices from the server') +
             PTAG('xos.slices                          get the slices that were fetched');

  },

  _tutorial: function() {
    this._tutorialPtr = 0;
    return PTAG("This is a self-guided tutorial on the xos shell.") +
           PTAG("The tutorial is simple, more or less a few basic commands to try.") +
           PTAG("To go directly to any part tutorial, enter one of the commands t0, t1, t2...t10") +
           PTAG("Otherwise, use 'next' and 'back'. Start by typing 'next' and pressing enter.");
  },

  // go to the next step in the tutorial.
  _next: function() {
    if(this._tutorialPtr < this._tutorialMax) {
      return this['_t' + (this._tutorialPtr + 1)]();
    }
    else {
      return "You've reached the end of the tutorial. To go to the beginning, type 'tutorial'";
    }
  },

  // go to the previous step in the tutorial.
  _back: function() {
    if(this._tutorialPtr > 1) {
      return this['_t' + (this._tutorialPtr - 1)]();
    }
    else {
      return this._tutorial();
    }
  },

  _t1: function() {
    this._tutorialPtr = 1;
    return PTAG('1. JavaScript Shell') +
           PTAG('The first thing to notice is that the MongoDB shell is JavaScript-based.') +
           PTAG('So you can do things like:') +
           PTAG('  a = 5; ') +
           PTAG('  a * 10; ') +
           PTAG('  print(a); ') +
           PTAG("  for(i=0; i<10; i++) { print('hello'); }; ") +
           PTAG("Try a few JS commands; when you're ready to move on, enter 'next'");

  },

  _t2: function() {
    this._tutorialPtr = 2;
    return PTAG('2. Reading from the server is asynchronous') +
           PTAG('Try these:') +
           PTAG('    xos.slices.models;') +
           PTAG('    // the above should have printed empty list') +
           PTAG('    xos.slices.fetch();') +
           PTAG('    // wait a second or two...') +
           PTAG('    xos.slices.models;');

  },

  _t3: function() {
    this._tutorialPtr = 3;
    return PTAG('3. Responding to events') +
           PTAG('Try these:') +
           PTAG('    xos.slices.fetch();') +
           PTAG('    tmp=xos.slices.on("change", function() { alert("woot!"); });') +
           PTAG('    xos.slices.models[0].set("description", "somerandomtext");');

  },

  _t4: function() {
    this._tutorialPtr = 4;
    return PTAG('4. Available xos objects and methods') +
           PTAG('Try these:') +
           PTAG('    xos.listObjects();') +
           PTAG('    xos.slices.listMethods();');

  },

  _getCommand: function(tokens) {
    if(tokens[0] && ArrayInclude(MongoKeywords,(tokens[0].value + '').toLowerCase())) {
      switch(tokens[0].value.toLowerCase()) {
        case 'help':
          return this._help;

        case 'tutorial':
          return this._tutorial;
        case 'next':
          return this._next;
        case 'back':
          return this._back;
        case 't0':
          return this._tutorial;
        case 't1':
          return this._t1;
        case 't2':
          return this._t2;
        case 't3':
          return this._t3;
        case 't4':
          return this._t4;
      }
    }
  }
};

function replaceAll(find, replace, str) {
  return str.replace(new RegExp(find, 'g'), replace);
}

/* stackoverflow: http://stackoverflow.com/questions/4810841/how-can-i-pretty-print-json-using-javascript */
function syntaxHighlight(json) {
    if ( json.hasOwnProperty("__str__")) {
        return syntaxHighlight(json.__str__());
    }
    if (typeof json != 'string') {
         json = JSON.stringify(json, undefined, "\t");
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'terminal_number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'terminal_key';
            } else {
                cls = 'terminal_string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'terminal_boolean';
        } else if (/null/.test(match)) {
            cls = 'terminal_null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

$htmlFormat = function(obj) {
  //JSON.stringify(obj,undefined,2)
  result=replaceAll("\t","&nbsp;",replaceAll("\n","<br>",syntaxHighlight(obj))); //tojson(obj, ' ', ' ', true);
  return result;
}

function startTerminal() {
  var mongo       = new MongoHandler();
  var terminal    = new ReadLine({htmlForInput: DefaultInputHtml,
                                  handler: mongo._process,
                                  scoper: mongo});
  $("#terminal_help1").show();
  $("#terminal_help2").show();
  $("#terminal_wait").hide();

  $("#terminal").bind('click', function() { $(".readLine.active").focus(); });
};

$(document).ready(function() {
    startTerminal();
});
