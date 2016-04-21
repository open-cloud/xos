/**
 * © OpenCORD
 *
 * Created by teone on 4/15/16.
 */

(function () {
  'use strict';

  describe('The xos.helper module', function(){
    describe('The xos-alert component', () => {

      let element, scope, isolatedScope;

      let message = 'Test Error Message';

      beforeEach(module('xos.helpers'));

      it('should throw an error if no config is specified', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          $compile(angular.element('<xos-alert></xos-alert>'))($rootScope);
          $rootScope.$digest();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosAlert] Please provide a configuration via the "config" attribute'));
      }));

      describe('when correctly configured', () => {
        beforeEach(inject(($compile, $rootScope) => {

          scope = $rootScope.$new();

          scope.config = {
            type: 'danger',
            closeBtn: true
          };

          element = angular.element(`<xos-alert config="config">${message}</xos-alert>`);
          $compile(element)(scope);
          scope.$digest();
          isolatedScope = element.isolateScope().vm;
        }));

        it('should transclude the message', () => {
          let textContainer = element[0].getElementsByTagName('p')[0];
          let text = angular.element(textContainer).text();
          expect(text).toEqual(message)
        });

        it('should have a close button', () => {
          let btn = element[0].getElementsByTagName('button');
          expect(btn.length).toEqual(1);
        });

        describe('when the close button is clicked', () => {
          it('should hide the alert', () => {
            let btn = element[0].getElementsByTagName('button')[0];
            btn.click();
            let alert = angular.element(element[0].querySelectorAll('.alert')[0]);
            expect(alert.hasClass('ng-hide')).toBeTruthy();
          });
        });

        describe('when autoHide is set', () => {

          let to;

          beforeEach(inject(($compile, $rootScope, $timeout) => {
            scope = $rootScope.$new();

            scope.config = {
              type: 'danger',
              closeBtn: true,
              autoHide: 500
            };

            to = $timeout;

            element = angular.element(`<xos-alert config="config">${message}</xos-alert>`);
            $compile(element)(scope);
            scope.$digest();
            isolatedScope = element.isolateScope().vm;
          }));

          it('should hide the alert', () => {
            to.flush();
            expect(isolatedScope.show).toBeFalsy();
            let alert = angular.element(element[0].querySelectorAll('.alert')[0]);
            expect(alert.hasClass('ng-hide')).toBeTruthy();
          });
        });

        describe('when show is set to false', () => {

          beforeEach(inject(($compile, $rootScope) => {
            scope = $rootScope.$new();

            scope.config = {
              type: 'danger',
              closeBtn: true
            };

            scope.show = false;

            element = angular.element(`<xos-alert config="config" show="show">${message}</xos-alert>`);
            $compile(element)(scope);
            scope.$digest();
            isolatedScope = element.isolateScope().vm;
          }));

          it('should hide the alert', () => {
            let alert = angular.element(element[0].querySelectorAll('.alert')[0]);
            expect(alert.hasClass('ng-hide')).toBeTruthy();
          });

          describe('when show is changed to true', () => {
            beforeEach(() => {
              scope.show = true;
              scope.$digest();
            });

            it('should show the alert', () => {
              let alert = angular.element(element[0].querySelectorAll('.alert')[0]);
              expect(alert.hasClass('ng-hide')).toBeFalsy();
            });
          });
        });

      });
    });
  });
})();