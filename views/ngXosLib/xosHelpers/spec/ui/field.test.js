/**
 * © OpenCORD
 *
 * Created by teone on 5/25/16.
 */

(function () {
  'use strict';

  let element, scope, isolatedScope, rootScope, compile;
  const compileElement = () => {

    if(!scope){
      scope = rootScope.$new();
    }

    element = angular.element('<xos-field name="name" field="field" ng-model="ngModel"></xos-field>');
    compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }

  describe('The xos.helper module', function(){

    describe('The xosField component', () => {

      beforeEach(module('xos.helpers'));

      beforeEach(inject(function ($compile, $rootScope) {
        compile = $compile;
        rootScope = $rootScope;
      }));

      it('should throw an error if no name is passed', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          scope = $rootScope.$new();
          scope.field = {
            label: 'Label',
            type: 'number',
            validators: {}
          };
          scope.ngModel = {
            label: 1
          };
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosField] Please provide a field name'));
      }));

      it('should throw an error if no field definition is passed', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          scope = $rootScope.$new();
          scope.name = 'label';
          scope.ngModel = {
            label: 1
          };
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosField] Please provide a field definition'));
      }));

      it('should throw an error if no field model is passed', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          scope = $rootScope.$new();
          scope.name = 'label';
          scope.field = {
            label: 'Label',
            type: 'number',
            validators: {}
          };
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosField] Please provide an ng-model'));
      }));
    });
  });
})();