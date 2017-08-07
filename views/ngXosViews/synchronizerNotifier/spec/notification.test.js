
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

describe('The Synchronizer Notification Panel', () => {
  
  var scope, element, isolatedScope, XosUserPrefs;
  const xosNotification = {
    notify: jasmine.createSpy('notify')
  };

  const failureEvent = {
    name: 'test',
    status: false
  };

  const successEvent = {
    name: 'test',
    status: true
  };

  beforeEach(module('xos.synchronizerNotifier', ($provide) => {
    $provide.value('Diag', {
      start: () => null
    });

    $provide.value('xosNotification', xosNotification);
  }));
  beforeEach(module('templates'));

  beforeEach(inject(function($compile, $rootScope, _XosUserPrefs_){

    XosUserPrefs = _XosUserPrefs_;
    scope = $rootScope.$new();
    element = angular.element('<sync-status></sync-status>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }));

  describe('when an event is received', () => {

    beforeEach(() => {
      xosNotification.notify.calls.reset()
    });

    describe('and notification have not been sent', () => {
      
      beforeEach(() => {
        XosUserPrefs.setSynchronizerNotificationStatus('test', false);
        scope.$emit('diag', failureEvent);
      });

      it('should trigger notification', () => {
        expect(xosNotification.notify).toHaveBeenCalled();
      });

      it('should update status in the scope', () => {
        expect(isolatedScope.synchronizers.test).toEqual(failureEvent);
        scope.$emit('diag', successEvent);
        expect(isolatedScope.synchronizers.test).toEqual(successEvent);
      });
    });

    describe('and notification have been sent', () => {
      
      beforeEach(() => {
        XosUserPrefs.setSynchronizerNotificationStatus('test', true);
        scope.$emit('diag', failureEvent);
      });

      it('should not trigger multiple notification for the same synchronizer', () => {
        expect(xosNotification.notify).not.toHaveBeenCalled();
      });
    });
  });

});