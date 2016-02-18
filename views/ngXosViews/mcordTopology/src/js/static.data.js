'use strict';

angular.module('xos.mcordTopology')
.constant('TopologyElements', {
  nodes: [
    {
      id: 'fabric1',
      type: 'fabric',
      name: 'fabric1',
      fixed: true,
      x: 1,
      y: 1
    },
    {
      id: 'fabric2',
      type: 'fabric',
      name: 'fabric2',
      fixed: true,
      x: 1,
      y: 2
    },
    {
      id: 'fabric3',
      type: 'fabric',
      name: 'fabric3',
      fixed: true,
      x: 2,
      y: 1
    },
    {
      id: 'fabric4',
      type: 'fabric',
      name: 'fabric4',
      fixed: true,
      x: 2,
      y: 2
    }
  ],
  links: [
    {
      source: 'fabric1',
      target: 'fabric2'
    },
    {
      source: 'fabric1',
      target: 'fabric4'
    },
    {
      source: 'fabric3',
      target: 'fabric4'
    },
    {
      source: 'fabric3',
      target: 'fabric2'
    }
  ]
})