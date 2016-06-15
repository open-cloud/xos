/**
 * © OpenCORD
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  let mockData;

  describe('The xos.helper module', function(){
    describe('The xos-smart-table component', () => {

      var spy, emptySpy, scope, isolatedScope, element;

      beforeEach(module('xos.helpers'));

      beforeEach(function() {

        // set mockData
        mockData = [
          {
            id: 1,
            first_name: 'Jon',
            last_name: 'Snow',
            hidden_field: 'hidden'
          }
        ];

        jasmine.addMatchers({
          toBeInstanceOf: function() {

            return {
              compare: (actual, expected) => {
                var actual = actual;
                var result = {};
                result.pass = actual instanceof expected.constructor;

                result.message = 'Expected ' + actual + ' to be instance of ' + expected;

                return result;
              },
              negativeCompare: (actual, expected) => {
                var actual = actual;
                var result = {};
                result.pass = actual instanceof expected.constructor === false;

                result.message = 'Expected ' + actual + ' to be instance of ' + expected;

                return result;
              }
            }
          }
        });
      });

      // mock the service
      beforeEach(function(){
        module(function($provide){
          $provide.service('MockResource', function(){
            return {
              query: '',
              delete: ''
            }
          });

          $provide.service('EmptyResource', function(){
            return {
              query: ''
            }
          });
        });
      })

      beforeEach(inject(function ($compile, $rootScope, $q, MockResource) {
        scope = $rootScope.$new();

        scope.config = {
          resource: 'MockResource',
          hiddenFields: ['hidden_field']
        };

        spy = MockResource;

        spyOn(MockResource, 'query').and.callFake(function() {
          var deferred = $q.defer();
          deferred.resolve(mockData);
          return {$promise: deferred.promise};
        });

        spyOn(MockResource, 'delete').and.callFake(function() {
          var deferred = $q.defer();
          deferred.resolve();
          return {$promise: deferred.promise};
        });

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
        // the 4th field is the mocked save method
        expect($(element).find('thead th').length).toEqual(3);
        expect($(element).find('thead th')[0]).toContainText('First name:');
        expect($(element).find('thead th')[1]).toContainText('Last name:');
        expect($(element).find('thead th')[2]).toContainText('Actions:');
      });

      it('should delete a model', () => {
        // saving mockData (they are going to be deleted)
        let mock = angular.copy(mockData);
        $(element).find('a[title="delete"]')[0].click();
        expect(spy.delete).toHaveBeenCalledWith({id: mock[0].id});
        expect($(element).find('.alert')).toContainText(`MockResource with id ${mock[0].id} successfully deleted`);
      });

      it('should show the form', () => {
        expect($(element).find('.panel')[0]).toHaveClass('ng-hide');
        $(element).find('a[title="details"]')[0].click();
        expect($(element).find('.panel')).not.toHaveClass('ng-hide');
      });

      it('should hide the form', () => {
        isolatedScope.detailedItem = {
          some: 'model'
        };
        scope.$apply();
        expect($(element).find('.panel')).not.toHaveClass('ng-hide');
        $(element).find('.panel .col-xs-1 a')[0].click();
        expect($(element).find('.panel')[0]).toHaveClass('ng-hide');
      });

      it('should save an item', inject(($q) => {

        let model = {
          id: 1,
          first_name: 'Jon',
          last_name: 'Snow',
          hidden_field: 'hidden',
          $save: '',
          $update: ''
        };

        spyOn(model, '$save').and.callFake(function() {
          var deferred = $q.defer();
          deferred.resolve();
          return deferred.promise;
        });

        spyOn(model, '$update').and.callFake(function() {
          var deferred = $q.defer();
          deferred.resolve();
          return deferred.promise;
        });

        isolatedScope.detailedItem = model;
        scope.$apply();
        $(element).find('xos-form .btn.btn-success').click();
        expect(model.$update).toHaveBeenCalled();
      }));

      it('should have an add button', () => {
        let addBtn = $(element).find('.row .btn.btn-success');
        expect(addBtn.parent().parent()).not.toHaveClass('ng-hide');
      });

      describe('when the add button is clicked', () => {
        beforeEach(() => {
          let btn = $(element).find('.row .btn.btn-success')
          btn[0].click();
        });

        xit('should create a new model', () => {
          expect(isolatedScope.detailedItem).toBeDefined();
          expect(isolatedScope.detailedItem).toBeInstanceOf('Resource');
        });
      });

      describe('when fetching an empty collection', () => {
        beforeEach(inject(function ($compile, $rootScope, $q, EmptyResource) {
          scope = $rootScope.$new();

          scope.config = {
            resource: 'EmptyResource'
          };

          emptySpy = EmptyResource;

          spyOn(EmptyResource, 'query').and.callFake(function() {
            var deferred = $q.defer();
            deferred.resolve([]);
            return {$promise: deferred.promise};
          });

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

        it('should not have an add button', () => {
          let addBtn = $(element).find('.row .btn.btn-success');
          expect(addBtn.parent().parent()).toHaveClass('ng-hide');
        });
      });


    });
  });
})();