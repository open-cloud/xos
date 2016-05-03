'use strict';

const expect = require('chai').expect;
const parser = require('./blueprintToNgResource');
const util = require('util');

const simpleResource = require('./mocks/basicResource');

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
      console.log(endpointObj);
      expect(endpointObj).to.have.lengthOf(2);
      expect(endpointObj).to.eql(expected);
    });
  });
});