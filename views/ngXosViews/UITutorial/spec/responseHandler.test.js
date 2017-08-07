
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


'use strict';

describe('The ResponseHandler service', () => {
  
  var ResponseHandler, done;

  beforeEach(module('xos.UITutorial'));
  beforeEach(module('templates'));

  beforeEach(inject(function (_ResponseHandler_) {
    // The injector unwraps the underscores (_) from around the parameter names when matching
    ResponseHandler = _ResponseHandler_;
    done = jasmine.createSpy('done');
  }));

  describe('the parse method', () => {
    it('should return an html template for a collection', () => {
      const collection = [
        {id: 1, deleted: true, name: 'one'},
        {id: 2, deleted: true, name: 'two'}
      ];

      const collectionHtml = `
      <div>
        <p>Corresponding js code: <code>jsCode</code></p>
        <div class="json"><div class="jsonCollection">[<div class="jsonObject">{"id":1,"name":"one"},</code></div><div class="jsonObject">{"id":2,"name":"two"}</code></div>]</div></div>
      </div>
    `;
      ResponseHandler.parse(collection, 'jsCode', done);
      expect(done).toHaveBeenCalledWith(collectionHtml)
    });

    it('should return an html template for an object', () => {
      const object = {id: 1, deleted: true, name: 'one'};

      const objectHtml = `
      <div>
        <p>Corresponding js code: <code></code></p>
        <div class="json"><div class="jsonObject">{"id":1,"name":"one"}</code></div></div>
      </div>
    `;
      ResponseHandler.parse(object, '', done);
      expect(done).toHaveBeenCalledWith(objectHtml)
    });
  });
});