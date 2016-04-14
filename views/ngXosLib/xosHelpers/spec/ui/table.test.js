/**
 * © OpenCORD
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  describe('The xos.helper module', function(){
    describe('The xos-table component', () => {

      beforeEach(module('xos.helpers'));

      it('should throw an error if no config is specified', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          $compile(angular.element('<xos-table></xos-table>'))($rootScope);
          $rootScope.$digest();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosTable] Please provide a configuration via the "config" attribute'));
      }));

      it('should throw an error if no config columns are specified', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          let scope = $rootScope.$new();
          scope.config = 'green';
          $compile(angular.element('<xos-table config="config"></xos-table>'))(scope);
          $rootScope.$digest();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosTable] Please provide a columns list in the configuration'));
      }));

    });

    describe('when correctly configured', function() {
      var scope, element, isolatedScope;

      beforeEach(inject(function ($compile, $rootScope) {
        scope = $rootScope.$new();

        scope.config = {
          columns: [
            {
              label: 'Label 1',
              prop: 'label-1'
            },
            {
              label: 'Label 2',
              prop: 'label-2'
            }
          ]
        };

        scope.data = [
          {
            'label-1': 'Sample 1.1',
            'label-2': 'Sample 1.2'
          },
          {
            'label-1': 'Sample 2.1',
            'label-2': 'Sample 2.2'
          }
        ]

        element = angular.element('<xos-table config="config" data="data"></xos-table>');
        $compile(element)(scope);
        // scope.$apply();
        element.scope().$apply();
        isolatedScope = element.isolateScope();
        console.log(element, isolatedScope);
      }));

      xit('should contain 2 columns', function() {
        console.log('aaa', isolatedScope);
        
        // one is the filter, the other two are the products, one is the pagination
        expect(isolatedScope.columns).toEqual(2);
      });
    });
  });
})();

