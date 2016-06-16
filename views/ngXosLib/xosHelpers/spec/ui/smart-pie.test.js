/**
 * © OpenCORD
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  let mockData, compile, rootScope, spy, scope, isolatedScope, element, interval;

  const compileElement = () => {

    if(!scope){
      scope = rootScope.$new();
    }

    element = angular.element('<xos-smart-pie config="config"></xos-smart-pie>');
    compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }

  describe('The xos.helper module', function(){
    describe('The xos-smart-pie component', () => {
      
      beforeEach(module('xos.helpers'));

      beforeEach(function(){
        module(function($provide){
          $provide.service('MockResource', function(){
            return {
              query: ''
            }
          });
        });
      });

      beforeEach(inject(function ($compile, $rootScope) {

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

        compile = $compile;
        rootScope = $rootScope;
      }));

      it('should throw an error if no resource and no data are passed in the config', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          scope = $rootScope.$new();
          scope.config = {};
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosSmartPie] Please provide a resource or an array of data in the configuration'));
      }));

      describe('when data are passed in the configuration', () => {
        beforeEach(inject(function ($compile, $rootScope) {
          scope = $rootScope.$new();

          scope.config = {
            data: mockData,
            groupBy: 'category',
            classes: 'my-test-class'
          };

          compileElement();
        }));
        

        it('should attach provided classes', () => {
          expect($(element).find('canvas')).toHaveClass('my-test-class');
        });

        it('should group elements', () => {
          let groupedData = [2, 1];
          expect(isolatedScope.data).toEqual(groupedData);
        });

        describe('when a labelFormatter function is provided', () => {
          beforeEach(() => {
            scope.config.labelFormatter = (labels) => {
              return labels.map(l => l === '1' ? 'First' : 'Second');
            };
            compileElement();
          });
          it('should format labels', () => {
            expect(isolatedScope.labels).toEqual(['First', 'Second'])
          });
        });

        describe('when provided data changes', () => {
          beforeEach(() => {
            scope.config.data.push({
              id: 2,
              first_name: 'Danaerys',
              last_name: 'Targaryen',
              category: 1
            });
            scope.$digest();
          });
          it('should calculate again the data', () => {
            expect(isolatedScope.data).toEqual([3, 1]);
          });
        });
      });

      
      describe('when a resource is specified in the configuration', () => {

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

          compileElement();
        }));


        it('should call the server and group elements', () => {
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
            compileElement();
          }));

          it('should format labels', () => {
            expect(isolatedScope.labels).toEqual(['First', 'Second'])
          });
        });

        describe('when polling is enabled', () => {
          beforeEach(inject(function ($compile, $rootScope, $interval){

            //mocked $interval (by ngMock)
            interval = $interval;

            // cleaning the spy
            spy.query.calls.reset()

            scope = $rootScope.$new();
            scope.config = {
              resource: 'MockResource',
              groupBy: 'category',
              classes: 'label-formatter-test',
              poll: 2
            };
            compileElement();
          }));

          it('should call the backend every 2 second', () => {
            expect(spy.query).toHaveBeenCalled();
            expect(spy.query.calls.count()).toEqual(1);
            interval.flush(2000);
            expect(spy.query.calls.count()).toEqual(2);
            interval.flush(2000);
            expect(spy.query.calls.count()).toEqual(3)
          });
        });
      });


    });
  });
})();