'use strict';

describe('In Ceilometer View', () => {

  var scope, element, vm, httpBackend;

  beforeEach(module('xos.ceilometerDashboard'));
  beforeEach(module('templates'));

  beforeEach(inject(($httpBackend, $rootScope) => {
    httpBackend = $httpBackend;
    scope = $rootScope.$new();
  }))

  describe('The dashboard', () => {
    beforeEach(inject(function($httpBackend, $compile){
      element = angular.element('<ceilometer-dashboard></ceilometer-dashboard>');
      $compile(element)(scope);
      scope.$digest();
      vm = element.isolateScope().vm;
      httpBackend.flush();
    }));

    xdescribe('when loading service list', () => {
      it('should append the list to the scope', () => {
        expect(vm.services.length).toBe(2);
        expect(vm.services[0].slices.length).toBe(2);
        expect(vm.services[1].slices.length).toBe(2);
      });
    });

    xdescribe('when a slice is selected', () => {
      it('should load corresponding meters', () => {
        vm.loadSliceMeter(vm.services[0].slices[0]);

        httpBackend.flush();

        expect(vm.selectedSlice).toEqual('slice-a-1');
        expect(vm.selectedTenant).toEqual('id-a-1');

        expect(Object.keys(vm.selectedResources).length).toBe(2);
        expect(vm.selectedResources['resource-1'].length).toBe(2);
        expect(vm.selectedResources['resource-2'].length).toBe(1);
      });
    });
  });

  describe('the sample view', () => {
    beforeEach(inject(function($httpBackend, $compile, $stateParams){

      $stateParams.name = 'fakeName';
      $stateParams.tenant = 'fakeTenant';

      element = angular.element('<ceilometer-samples></ceilometer-samples>');
      $compile(element)(scope);
      scope.$digest();
      vm = element.isolateScope().vm;
      httpBackend.flush();
    }));

    it('should group samples by resource_id', () => {
      expect(Object.keys(vm.samplesList.fakeTenant).length).toBe(2)
      expect(Object.keys(vm.samplesList.anotherTenant).length).toBe(3)
      expect(Object.keys(vm.samplesList.thirdTenant).length).toBe(1)
    });

    xit('should add the comparable samples to the dropdown list', () => {
      console.log(vm.sampleLabels);
      expect(vm.sampleLabels[0].id).toEqual('anotherTenant')
      expect(vm.sampleLabels[1].id).toEqual('thirdTenant')
    });

    it('should add the selected meter to the chart', () => {
      expect(vm.chart.labels.length).toBe(2);
      expect(vm.chart.series[0]).toBe('fakeTenant');
      expect(vm.chart.data[0].length).toBe(2);
      expect(vm.chart.data[0][0]).toBe(110);
      expect(vm.chart.data[0][1]).toBe(120);
      expect(vm.chartMeters[0].resource_id).toBe('fakeTenant')
      expect(vm.chartMeters[0].resource_name).toBe('fakeName')
    });

    it('should add a sample to the chart', () => {
      vm.addMeterToChart('anotherTenant');
      expect(vm.chart.labels.length).toBe(3);
      expect(vm.chart.data[1].length).toBe(3);
      expect(vm.chart.data[1][0]).toBe(210);
      expect(vm.chart.data[1][1]).toBe(220);
      expect(vm.chart.data[1][2]).toBe(230);
      expect(vm.chartMeters[1].resource_id).toBe('anotherTenant')
      expect(vm.chartMeters[1].resource_name).toBe('anotherName')
    });

    it('should remove a sample from the chart', () => {
      // for simplyvity add a tenant (it's tested)
      vm.addMeterToChart('anotherTenant');
      vm.removeFromChart(vm.chartMeters[0]);
      expect(vm.chart.data[0].length).toBe(3);
      expect(vm.chart.data[0][0]).toBe(210);
      expect(vm.chart.data[0][1]).toBe(220);
      expect(vm.chart.data[0][2]).toBe(230);
      expect(vm.chartMeters[0].resource_id).toBe('anotherTenant')
      expect(vm.chartMeters[0].resource_name).toBe('anotherName')
    });

    describe('The format sample labels method', () => {
      xit('should create an array of unique labels', () => {
        // unique because every resource has multiple samples (time-series)
        const samples = [
          {resource_id: 1, resource_name: 'fakeName'},
          {resource_id: 1, resource_name: 'fakeName'},
          {resource_id: 2, resource_name: 'anotherName'},
          {resource_id: 2, resource_name: 'anotherName'}
        ];

        const result = vm.formatSamplesLabels(samples);

        expect(result.length).toBe(2);
        expect(result[0]).toEqual({id: 1, name: 'fakeName'});
        expect(result[1]).toEqual({id: 2, name: 'anotherName'});
      });
    });
  });
});