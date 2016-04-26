/**
 * © OpenCORD
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  describe('The xos.helper module', function(){
    describe('The xos-smart-table component', () => {

      let spy, scope, isolatedScope, element;

      beforeEach(module('xos.helpers'));

      // mock the service
      beforeEach(function(){
        module(function($provide){
          $provide.service('MockResource', function(){
            this.test = (msg) => console.log(msg);
            this.query = jasmine.createSpy('add')
              .and.returnValue({$promise: cb => {
                console.log('------------------ CB ------------------');
                return cb([]);
              }});
          });
        });
      })

      beforeEach(inject(function ($compile, $rootScope, MockResource) {
        scope = $rootScope.$new();

        scope.config = {
          resource: 'MockResource'
        };

        spy = MockResource;
        // console.log(MockResource.query.toString(), spy.query.toString());

        element = angular.element('<xos-smart-table config="config"></xos-smart-table>');
        $compile(element)(scope);
        scope.$digest();
        isolatedScope = element.isolateScope().vm;
      }));

      it('should query elements', () => {

        console.log(spy.query.toString());
        expect(spy.query).toHaveBeenCalled();
      });

    });
  });
})();