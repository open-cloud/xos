'use strict';

const expect = require('chai').expect;
const parser = require('./blueprintToNgResource');
const util = require('util');

const simpleResource = require('./mocks/basicResource');
const complexResource = require('./mocks/complexResource');

describe('When parsing blueprint API definitions', () => {

  describe('the find common string method', () => {
    let lists = [
      {data: ['Instances-collection', 'Instances-detail'], expect: 'Instances-'},
      {data: ['/api/core/instances/:id', '/api/core/instances/'], expect: '/api/core/instances/'}
    ];
    lists.forEach(list =>
      it('should return the common string in an array of string', () => {
        let res = parser.findCommonString(list.data);
        expect(res).to.equal(list.expect)
      })
    )
  });

  describe('the url formatter', () => {
    it('should strip optional params', () => {
      let formatted = parser.formatHref('/api/core/instances/{?no_hyperlinks}');
      expect(formatted).to.equal('/api/core/instances/')
    });

    it('should maintain params', () => {
      let formatted = parser.formatHref('/api/core/instances/{id}');
      expect(formatted).to.equal('/api/core/instances/:id')
    });
  });

  describe('the get params', () => {
    it('should return an empty string if no param', () => {
      let formatted = parser.getParamName('/api/core/instances/');
      expect(formatted).to.equal('')
    });

    it('should maintain params', () => {
      let formatted = parser.getParamName('/api/core/instances/:id');
      expect(formatted).to.equal('id')
    });
  });

  describe('the getBaseUrl', () => {

    it('should return the common path without params', () => {
      // NOTE not sure if we need this
      let group = [
        {
          name: 'Instances-Collection',
          param: { href: '/api/core/instances/', name: '' }
        },
        {
          name: 'Instances-Detail',
          param: { href: '/api/core/instances/somehting/', name: 'id' }
        }
      ];
      let res = parser.getBaseUrl(group);
      expect(res).to.eql({href: '/api/core/instances/', param: ''});
    });

    it('should return the common path with params', () => {
      let group = [
        {
          name: 'Instances-Collection',
          param: { href: '/api/core/instances/', name: '' }
        },
        {
          name: 'Instances-Detail',
          param: { href: '/api/core/instances/:id/', name: 'id' }
        }
      ];
      let res = parser.getBaseUrl(group);
      expect(res).to.eql({href: '/api/core/instances/:id/', param: 'id'});
    });

    it('should return the common path with params', () => {
      let group = [
        {
          name: 'Instances-Detail',
          param: { href: '/api/core/instances/:id/', name: 'id' }
        }
      ];
      let res = parser.getBaseUrl(group);
      expect(res).to.eql({href: '/api/core/instances/:id/', param: 'id'});
    });
  });

  describe('the loopApiEndpoint', () => {

    describe('for a simple resource', () => {
      let expected = [
        {
          name: 'Instances-Collection',
          param: { href: '/api/core/instances/', name: '' }
        },
        {
          name: 'Instances-Detail',
          param: { href: '/api/core/instances/:id/', name: 'id' }
        }
      ];

      it('should return a list of endpoints for a group', () => {
        let endpointObj = parser.loopApiEndpoint(simpleResource[0].content);
        expect(endpointObj).to.have.lengthOf(2);
        expect(endpointObj).to.eql(expected);
      });
    });

    describe('for a complex resource', () => {

      let expected = [
        {
          name: 'Subscribers-Collection',
          param: {
            href: '/api/tenant/cord/subscriber/',
            name: ''
          }
        },
        {
          name: 'Subscribers-Detail',
          param: {
            href: '/api/tenant/cord/subscriber/:id/',
            name: 'id'
          }
        },
        {
          name: 'Subscriber-features',
          param: {
            href: '/api/tenant/cord/subscriber/:id/features/',
            name: 'id'
          }
        },
        {
          name: 'Subscriber-features-uplink_speed',
          param: {
            href: '/api/tenant/cord/subscriber/:id/features/uplink_speed/',
            name: 'id'
          }
        },
        {
          name: 'Subscriber-features-downlink_speed',
          param: {
            href: '/api/tenant/cord/subscriber/:id/features/downlink_speed/',
            name: 'id'
          }
        },
        {
          name: 'Subscriber-features-cdn',
          param: {
            href: '/api/tenant/cord/subscriber/:id/features/cdn/',
            name: 'id'
          }
        },
        {
          name: 'Subscriber-features-uverse',
          param: {
            href: '/api/tenant/cord/subscriber/:id/features/uverse/',
            name: 'id'
          }
        },
        {
          name: 'Subscriber-features-status',
          param: {
            href: '/api/tenant/cord/subscriber/:id/features/status/',
            name: 'id'
          }
        }
      ];

      describe('the getBaseUrl', () => {

        it('should return the common path with params', () => {
          let res = parser.getBaseUrl(expected);
          expect(res).to.eql({href: '/api/tenant/cord/subscriber/:id/', param: 'id'});
        });
      });

      it('should return a list of endpoints for a group', () => {
        let endpointObj = parser.loopApiEndpoint(complexResource[0].content);
        // console.log(endpointObj);
        expect(endpointObj).to.have.lengthOf(8);
        expect(endpointObj).to.eql(expected);
      });
    });
  });

  describe('the getGroupMethods', () => {

    it('should return a list of all the methods for a simple resource', () => {
      let res = parser.getGroupMethods(simpleResource[0].content, '/api/core/instances/:id/');

      expect(res).to.eql([])
    });

    it('should return a list of all the methods', () => {
      let res = parser.getGroupMethods(complexResource[0].content, '/api/tenant/cord/subscriber/:id/');
      expect(res).to.eql(
        [
          {
            method: 'GET',
            url: '/api/tenant/cord/subscriber/:id/features/',
            isArray: false,
            name: 'View-a-Subscriber-Features-Detail'
          },
          {
            method: 'GET',
            url: '/api/tenant/cord/subscriber/:id/features/uplink_speed/',
            isArray: false,
            name: 'Read-Subscriber-uplink_speed'
          },
          {
            method: 'PUT',
            url: '/api/tenant/cord/subscriber/:id/features/uplink_speed/',
            isArray: false,
            name: 'Update-Subscriber-uplink_speed'
          },
          {
            method: 'GET',
            url: '/api/tenant/cord/subscriber/:id/features/downlink_speed/',
            isArray: false,
            name: 'Read-Subscriber-downlink_speed'
          },
          {
            method: 'PUT',
            url: '/api/tenant/cord/subscriber/:id/features/downlink_speed/',
            isArray: false,
            name: 'Update-Subscriber-downlink_speed'
          },
          {
            method: 'GET',
            url: '/api/tenant/cord/subscriber/:id/features/cdn/',
            isArray: false,
            name: 'Read-Subscriber-cdn'
          },
          {
            method: 'PUT',
            url: '/api/tenant/cord/subscriber/:id/features/cdn/',
            isArray: false,
            name: 'Update-Subscriber-cdn'
          },
          {
            method: 'GET',
            url: '/api/tenant/cord/subscriber/:id/features/uverse/',
            isArray: false,
            name: 'Read-Subscriber-uverse'
          },
          {
            method: 'PUT',
            url: '/api/tenant/cord/subscriber/:id/features/uverse/',
            isArray: false,
            name: 'Update-Subscriber-uverse'
          },
          {
            method: 'GET',
            url: '/api/tenant/cord/subscriber/:id/features/status/',
            isArray: false,
            name: 'Read-Subscriber-status'
          },
          {
            method: 'PUT',
            url: '/api/tenant/cord/subscriber/:id/features/status/',
            isArray: false,
            name: 'Update-Subscriber-status'
          }
        ]
      );
    });
  });

  describe('the loopApiGroups method', () => {
    it('should return data to feed the handlebars template', () => {
      let res = parser.loopApiGroups(simpleResource);
      expect(res.Instances).to.eql(
        {
          description: '',
          baseUrl: { href: '/api/core/instances/:id/', param: 'id' },
          resourceName: 'Instances',
          ngModule: 'xos.helpers',
          customActions: []
        }
      );
    });

    it('should return data to feed the handlebars template for a complex resource', () => {
      let res = parser.loopApiGroups(complexResource);
      expect(res.Subscribers).to.eql(
        {
          description: '',
          baseUrl: { href: '/api/tenant/cord/subscriber/:id/', param: 'id' },
          resourceName: 'Subscribers',
          ngModule: 'xos.helpers',
          'customActions': [
            {
              'isArray': false,
              'method': 'GET',
              'name': 'View-a-Subscriber-Features-Detail',
              'url': '/api/tenant/cord/subscriber/:id/features/',
            },
            {
              'isArray': false,
              'method': 'GET',
              'name': 'Read-Subscriber-uplink_speed',
              'url': '/api/tenant/cord/subscriber/:id/features/uplink_speed/',
            },
            {
              'isArray': false,
              'method': 'PUT',
              'name': 'Update-Subscriber-uplink_speed',
              'url': '/api/tenant/cord/subscriber/:id/features/uplink_speed/',
            },
            {
              'isArray': false,
              'method': 'GET',
              'name': 'Read-Subscriber-downlink_speed',
              'url': '/api/tenant/cord/subscriber/:id/features/downlink_speed/',
            },
            {
              'isArray': false,
              'method': 'PUT',
              'name': 'Update-Subscriber-downlink_speed',
              'url': '/api/tenant/cord/subscriber/:id/features/downlink_speed/',
            },
            {
              'isArray': false,
              'method': 'GET',
              'name': 'Read-Subscriber-cdn',
              'url': '/api/tenant/cord/subscriber/:id/features/cdn/',
            },
            {
              'isArray': false,
              'method': 'PUT',
              'name': 'Update-Subscriber-cdn',
              'url': '/api/tenant/cord/subscriber/:id/features/cdn/',
            },
            {
              'isArray': false,
              'method': 'GET',
              'name': 'Read-Subscriber-uverse',
              'url': '/api/tenant/cord/subscriber/:id/features/uverse/',
            },
            {
              'isArray': false,
              'method': 'PUT',
              'name': 'Update-Subscriber-uverse',
              'url': '/api/tenant/cord/subscriber/:id/features/uverse/',
            },
            {
              'isArray': false,
              'method': 'GET',
              'name': 'Read-Subscriber-status',
              'url': '/api/tenant/cord/subscriber/:id/features/status/',
            },
            {
              'isArray': false,
              'method': 'PUT',
              'name': 'Update-Subscriber-status',
              'url': '/api/tenant/cord/subscriber/:id/features/status/',
            },
          ],
        }
      );
    });
  });
});