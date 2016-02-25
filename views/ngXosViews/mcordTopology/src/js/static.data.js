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
  ],
  icons: {
    switch: `M10,20a10,10,0,0,1,10-10h70a10,10,0,0,1,10,10v70a10,10,
            0,0,1-10,10h-70a10,10,0,0,1-10-10zM60,26l12,0,0-8,18,13-18,13,0
            -8-12,0zM60,60l12,0,0-8,18,13-18,13,0-8-12,0zM50,40l-12,0,0-8
            -18,13,18,13,0-8,12,0zM50,74l-12,0,0-8-18,13,18,13,0-8,12,0z`,
  }
})