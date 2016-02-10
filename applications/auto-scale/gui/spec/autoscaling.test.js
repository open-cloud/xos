'use strict';

describe('In autoscaling app', () => {
  var scope, element, vm, httpBackend, Service;



  beforeEach(module('autoscaling'));
  beforeEach(module('templates'));

  beforeEach(inject(($httpBackend, $rootScope, Autoscaling) => {
    httpBackend = $httpBackend;
    scope = $rootScope.$new();
    Service = Autoscaling;
  }));

  describe('the serviceContainer', () => {
    beforeEach(inject(function($httpBackend, $compile){
      
      httpBackend.whenGET('/autoscaledata').respond(200, autoscalingMock);

      element = angular.element('<service-container></service-container>');
      $compile(element)(scope);

      scope.$digest();
      vm = element.isolateScope().vm;
      httpBackend.flush();
    }));

    it('should correctly format data', () => {
      expect(vm.services['service1']).toBeDefined();
      expect(vm.services['service1']['slice1']).toBeDefined();
      expect(vm.services['service1']['slice1']['instance1']).toBeDefined();

      expect(vm.services['service1']['slice1']['instance1'][0].counter_volume).toBe(10);
      expect(vm.services['service1']['slice1']['instance1'][1].counter_volume).toBe(11);

      // triggering the function with 2 resources
      vm.printData(Service.formatData(autoscalingMock2instances));

      const keys = Object.keys(vm.services['service1']['slice1']);

      expect(vm.services['service1']['slice1'][keys[0]][0].counter_volume).toBe(10);
      expect(vm.services['service1']['slice1'][keys[0]][1].counter_volume).toBe(11);

    });
  });
});