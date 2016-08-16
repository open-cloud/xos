(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('LearnCmd', function(LessonInfo, $cookies, ErrorHandler){


    this.getCurrentLesson = (id,done)=>{
      var details = LessonInfo.lessonCatalogue(id);
      $cookies.put('lessonId', id);
      done(details.text);
    };

    this.nextLesson = (shell) => {
      this.shell = shell;
      shell.setCommandHandler('next', {
        exec: this.getNextLesson,
      });
    }

    this.printLesson = (shell) => {
      this.shell = shell;
      shell.setCommandHandler('print', {
        exec: this.printCurrentLesson,
      });
    };

    this.prevLesson = (shell) => {
      this.shell = shell;
      shell.setCommandHandler('prev', {
        exec: this.getPreviousLesson,
      });
    }

    this.getLessonIdFromCookie = ()=>{
      return $cookies.get('lessonId') ? parseInt($cookies.get('lessonId')) : -1;
    };

    this.getNextLesson = (cmd,arg,done)=>{
      let lessonId = this.getLessonIdFromCookie();
      return this.getCurrentLesson(lessonId+1,done)  ;
    };

    this.getPreviousLesson = (cmd,arg,done)=>{
      let lessonId = this.getLessonIdFromCookie();
      if(lessonId>0)  {
        this.getCurrentLesson(lessonId-1,done)
      }
      else {
        ErrorHandler.print(`This is the first Lesson`, done);
      }
    };

    this.printCurrentLesson = (cmd,args,done)=>{
      if (args[0]){
        this.getCurrentLesson(args[0], done);
      }
      else {
        let lessonId = this.getLessonIdFromCookie();
        if (lessonId > -1) {
          this.getCurrentLesson(lessonId, done)
        }
        else {
          ErrorHandler.print(`This is the first Lesson`, done);
        }
      }
    };

    this.setup = (shell) => {
      this.shell = shell;
      this.nextLesson(shell);
      this.prevLesson(shell);
      this.printLesson(shell);
    };

  });
})();