(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('LessonInfo', function(){

    this.lessonCatalogue = (id) => {
      let lessonData = [
        {
          id: 0,
          text: 'lesson 0 info',
          solution: 'Hello World'
        },
        {
          id: 1,
          text: 'lesson 1 info',
          solution: 'Hello World'
        },
        {
          id: 2,
          text: 'lesson 2 info',
          solution: 'Hello World'
        },
        {
          id: 3,
          text: 'lesson 3 info',
          solution: 'Hello World'
        },
        {
          id: 4,
          text: 'lesson 4 info',
          solution: 'Hello World  '
        },
        {
          id: 5,
          text: 'lesson 5 info',
          solution: 'Hello World'
        }
      ];
      return lessonData[id];
    }

  });
} )();