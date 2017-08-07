
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
  .service('ResponseHandler', function(TemplateHandler){

    const exclude = [
      'deleted',
      'enabled',
      'enacted',
      'exposed_ports',
      'lazy_blocked',
      'created',
      'validators',
      'controllers',
      'backend_status',
      'backend_register',
      'policed',
      'no_policy',
      'write_protect',
      'no_sync',
      'updated'
    ];

    this.parseObject = (obj, comma = '') => {
      obj = _.omit(obj, exclude);
      return TemplateHandler.jsonObject({'obj': obj, comma: comma});
    };

    this.parseCollection = (array) => {
      array = array.map((o, i) => `${this.parseObject(o, i === (array.length - 1) ? '':',')}`);
      return TemplateHandler.jsonCollection({'collection': array});
    };

    this.parse = (res, jsCode, done) => {
      if(_.isArray(res)) {
        res = this.parseCollection(res);
      }
      else{
        res = this.parseObject(res);
      }
      done(TemplateHandler.resourcesResponse({
        jsCode: jsCode,
        res: res
      }));
    };
  });
})();