(function () {
  'use strict';

  const meters = [
    {
      service: 'service-a',
      slice: 'slice-a-1',
      name: 'network.outgoing.packets.rate',
      resource_name: 'resource-1'
    },
    {
      service: 'service-a',
      slice: 'slice-a-1',
      name: 'network.incoming.packets.rate',
      resource_name: 'resource-1'
    },
    {
      service: 'service-a',
      slice: 'slice-a-1',
      name: 'network.incoming.packets.rate',
      resource_name: 'resource-2'
    }
  ];

  const samples = [
    {
      meter: 'cpu',
      resource_name: 'fakeName',
      resource_id: 'fakeTenant',
      timestamp: '2015-12-15T00:34:08',
      volume: 110
    },
    {
      meter: 'cpu',
      resource_name: 'fakeName',
      resource_id: 'fakeTenant',
      timestamp: '2015-12-15T00:44:08',
      volume: 120
    },
    {
      meter: 'cpu',
      resource_name: 'anotherName',
      resource_id: 'anotherTenant',
      timestamp: '2015-12-15T00:24:08',
      volume: 210
    },
    {
      meter: 'cpu',
      resource_name: 'anotherName',
      resource_id: 'anotherTenant',
      timestamp: '2015-12-15T00:34:08',
      volume: 220
    },
    {
      meter: 'cpu',
      resource_name: 'anotherName',
      resource_id: 'anotherTenant',
      timestamp: '2015-12-15T00:44:08',
      volume: 230
    },
    {
      meter: 'cpu',
      resource_name: 'thirdName',
      resource_id: 'thirdTenant',
      timestamp: '2015-12-15T00:44:08',
      volume: 310
    }
  ];

  const mapping = [
    {
      service: 'service-a',
      slices: [
        {
          project_id: 'id-a-1',
          slice: 'slice-a-1'
        },
        {
          project_id: 'id-a-2',
          slice: 'slice-a-2'
        }
      ]
    },
    {
      service: 'service-b',
      slices: [
        {
          project_id: 'id-b-1',
          slice: 'slice-b-1'
        },
        {
          project_id: 'id-b-2',
          slice: 'slice-b-2'
        }
      ]
    }
  ]

  angular.module('xos.ceilometerDashboard')
  .run(($httpBackend) => {
    $httpBackend.whenGET(/metersamples/).respond(samples);
    $httpBackend.whenGET(/xos-slice-service-mapping/).respond(mapping);
    $httpBackend.whenGET(/meters/).respond(meters);
  });
})();
