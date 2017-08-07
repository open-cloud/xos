
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

describe('The ErrorHandler service', () => {
  
  var ErrorHandler, done;

  beforeEach(module('xos.UITutorial'));
  beforeEach(module('templates'));

  beforeEach(inject(function (_ErrorHandler_) {
    // The injector unwraps the underscores (_) from around the parameter names when matching
    ErrorHandler = _ErrorHandler_;
    done = jasmine.createSpy('done');
  }));

  describe('the print method', () => {
    it('should return an html template', () => {
      ErrorHandler.print('myError', done);
      expect(done).toHaveBeenCalledWith(`<span class="error">[ERROR] myError</span>`)
    });
  });
});