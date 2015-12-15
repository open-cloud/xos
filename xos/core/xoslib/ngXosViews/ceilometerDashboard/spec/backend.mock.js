'use strict';
(function () {

  const meters = [
    // service_1
    //  - slice_1
    //    - resource_1
    // service_2
    //  - slice_2
    //    - resource_2
    //    - resource_3
    //  - slice_3
    //    - resource_4
    {
      service: 'service_1',
      slice: 'slice_1',
      resource_name: 'resource_1',
      resource_id: 'resource_id_1',
      name: 'instance_1',
      unit: 'instance'
    },
    {
      service: 'service_2',
      slice: 'slice_2',
      resource_name: 'resource_2',
      resource_id: 'resource_id_2',
      name: 'instance_2',
      unit: 'instance'
    },
    {
      service: 'service_2',
      slice: 'slice_2',
      resource_name: 'resource_3',
      resource_id: 'resource_id_3',
      name: 'instance_2',
      unit: 'instance'
    },
    {
      service: 'service_2',
      slice: 'slice_3',
      resource_name: 'resource_4',
      resource_id: 'resource_id_4',
      name: 'instance_3',
      unit: 'instance'
    }
  ];

  const samples = [
    {
      meter: 'cpu',
      resource_name: 'fakeName',
      project_id: 'fakeTenant',
      timestamp: '2015-12-15T00:34:08',
      volume: 110
    },
    {
      meter: 'cpu',
      resource_name: 'fakeName',
      project_id: 'fakeTenant',
      timestamp: '2015-12-15T00:44:08',
      volume: 120
    },
    {
      meter: 'cpu',
      resource_name: 'anotherName',
      project_id: 'anotherTenant',
      timestamp: '2015-12-15T00:24:08',
      volume: 210
    },
    {
      meter: 'cpu',
      resource_name: 'anotherName',
      project_id: 'anotherTenant',
      timestamp: '2015-12-15T00:34:08',
      volume: 220
    },
    {
      meter: 'cpu',
      resource_name: 'anotherName',
      project_id: 'anotherTenant',
      timestamp: '2015-12-15T00:44:08',
      volume: 230
    },
    {
      meter: 'cpu',
      resource_name: 'thirdName',
      project_id: 'thirdTenant',
      timestamp: '2015-12-15T00:44:08',
      volume: 310
    }
  ];

  angular.module('xos.ceilometerDashboard')
  .run(($httpBackend) => {
    $httpBackend.whenGET(/metersamples/).respond(samples);
    $httpBackend.whenGET(/meters/).respond(meters);
  });
})();
