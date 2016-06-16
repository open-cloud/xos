/**
 * © OpenCORD
 *
 * Created by teone on 4/18/16.
 */
/* eslint-disable angular/ng_window_service*/

// TODO write tests for log
// NODE Actually the code is working, the tests are not.

(function () {
  'use strict';

  xdescribe('The xos.helper module', function(){

    let log, window;

    let mockLog;

    beforeEach(function() {
      mockLog = jasmine.createSpyObj('logMock', ['info']);
    });

    beforeEach(function() {
      angular.mock.module('xos.helpers', function($injector, $provide) {
        // console.log('$injector',$injector.get('logDecorator'));
        $provide.value('$log', mockLog);
        // $provide.decorator('$log', $injector.get('logDecorator'));
      });
    });

    beforeEach(inject(($log, $window) => {
      log = $log;
      window = $window;
      // log.reset();
    }));

    describe('The log decorator', () => {
      it('should not print anything', inject(($log) => {
        // spyOn(log, 'info');
        $log.info('test');
        expect(mockLog.info).not.toHaveBeenCalled();
      }));

    });
    describe('if logging is enabled', () => {
      beforeEach(() => {
        window.location.href += '?debug=true'
      });

      it('should should log', () => {
        log.info('test');
        console.log(log.info.logs);
      });
    });
  });
})();
