
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