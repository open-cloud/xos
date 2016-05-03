/**
 * © OpenCORD
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  let mockData;

  describe('The xos.helper module', function(){
    describe('The xos-smart-pie component', () => {

      var spy, scope, isolatedScope, element;

      beforeEach(module('xos.helpers'));

      beforeEach(function() {

        // set mockData
        mockData = [
          {
            id: 1,
            first_name: 'Jon',
            last_name: 'Snow',
            category: 1
          },
          {
            id: 2,
            first_name: 'Danaerys',
            last_name: 'Targaryen',
            category: 2
          },
          {
            id: 3,
            first_name: 'Aria',
            last_name: 'Stark',
            category: 1
          }
        ]

      });

      // mock the service
      beforeEach(function(){
        module(function($provide){
          $provide.service('MockResource', function(){
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
          groupBy: 'category',
          classes: 'my-test-class'
        };

        spy = MockResource;

        spyOn(MockResource, 'query').and.callFake(function() {
          var deferred = $q.defer();
          deferred.resolve(mockData);
          return {$promise: deferred.promise};
        });

        element = angular.element('<xos-smart-pie config="config"></xos-smart-pie>');
        $compile(element)(scope);
        scope.$digest();
        isolatedScope = element.isolateScope().vm;
      }));

      it('should attach provided classes', () => {
        expect($(element).find('canvas')).toHaveClass('my-test-class');
      });

      it('should group elements', () => {
        let groupedData = [2, 1];
        expect(spy.query).toHaveBeenCalled();
        expect(isolatedScope.data).toEqual(groupedData);
      });

      describe('when a labelFormatter function is provided', () => {
        beforeEach(inject(function ($compile, $rootScope){
          scope = $rootScope.$new();
          scope.config = {
            resource: 'MockResource',
            groupBy: 'category',
            classes: 'label-formatter-test',
            labelFormatter: (labels) => {
              return labels.map(l => l === '1' ? 'First' : 'Second');
            }
          };
          element = angular.element('<xos-smart-pie config="config"></xos-smart-pie>');
          $compile(element)(scope);
          scope.$digest();
          isolatedScope = element.isolateScope().vm;
        }));

        it('should format labels', () => {
          expect(isolatedScope.labels).toEqual(['First', 'Second'])
        });
      });

    });
  });
})();