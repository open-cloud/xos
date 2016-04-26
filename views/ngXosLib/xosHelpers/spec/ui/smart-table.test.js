/**
 * © OpenCORD
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  const mockData = [
    {
      id: 1,
      first_name: 'Jon',
      last_name: 'Snow',
      hidden_field: 'hidden'
    }
  ];

  describe('The xos.helper module', function(){
    describe('The xos-smart-table component', () => {

      var spy, emptySpy, scope, isolatedScope, element;

      beforeEach(module('xos.helpers'));

      // mock the service
      beforeEach(function(){
        module(function($provide){
          $provide.service('MockResource', function(){
            this.query = jasmine.createSpy('query').and.callFake(() => {
              return {$promise: {then: (cb) => cb(mockData)}};
            });
          });

          $provide.service('EmptyResource', function(){
            this.query = jasmine.createSpy('emptyQuery').and.callFake(() => {
              return {$promise: {then: (cb) => cb([])}};
            });
          });
        });
      })

      beforeEach(inject(function ($compile, $rootScope, MockResource) {
        scope = $rootScope.$new();

        scope.config = {
          resource: 'MockResource',
          hiddenFields: ['hidden_field']
        };

        spy = MockResource;

        element = angular.element('<xos-smart-table config="config"></xos-smart-table>');
        $compile(element)(scope);
        scope.$digest();
        isolatedScope = element.isolateScope().vm;
      }));

      it('should query elements', () => {
        expect(spy.query).toHaveBeenCalled();
        expect($(element).find('.alert').parent().parent()).toHaveClass('ng-hide');
      });

      it('should hide hidden fields', () => {
        expect($(element).find('thead th').length).toEqual(2);
        expect($(element).find('thead th')[0]).toContainText('First name:');
        expect($(element).find('thead th')[1]).toContainText('Last name:');
      });

      describe('when fetching an empty collection', () => {
        beforeEach(inject(function ($compile, $rootScope, EmptyResource) {
          scope = $rootScope.$new();

          scope.config = {
            resource: 'EmptyResource'
          };

          emptySpy = EmptyResource;

          element = angular.element('<xos-smart-table config="config"></xos-smart-table>');
          $compile(element)(scope);
          scope.$digest();
          isolatedScope = element.isolateScope().vm;
        }));

        it('should display an alert', () => {
          expect(emptySpy.query).toHaveBeenCalled();
          expect($(element).find('.alert').parent().parent()).not.toHaveClass('ng-hide');
          expect($(element).find('.alert')).toContainText('No data to show');
        });
      });


    });
  });
})();