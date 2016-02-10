var autoscalingMock =[
  {
    'slice': 'slice1',
    'service': 'service1',
    'project_id': 'project1',
    'resources': {
      'resource1': {
        'queue': [
          {
            'timestamp': '2015-12-17T22:55:36Z',
            'counter_volume': 10,
          },
          {
            'timestamp': '2015-12-17T22:55:46Z',
            'counter_volume': 11,
          }
        ],
        'xos_instance_info': {
          'instance_name': 'instance1'
        }
      }
    }
  }
];

var autoscalingMock2instances =[
  {
    'slice': 'slice1',
    'service': 'service1',
    'project_id': 'project1',
    'resources': {
      'resource2': {
        'queue': [
          {
            'timestamp': '2015-12-17T22:55:36Z',
            'counter_volume': 20,
          },
          {
            'timestamp': '2015-12-17T22:55:46Z',
            'counter_volume': 21,
          }
        ],
        'xos_instance_info': {
          'instance_name': 'instance2'
        }
      },
      'resource1': {
        'queue': [
          {
            'timestamp': '2015-12-17T22:55:36Z',
            'counter_volume': 10,
          },
          {
            'timestamp': '2015-12-17T22:55:46Z',
            'counter_volume': 11,
          }
        ],
        'xos_instance_info': {
          'instance_name': 'instance1'
        }
      },
    }
  }
];