'use strict';

describe('The Service Relation Service', () => {
  
  var Service;

  beforeEach(module('xos.serviceTopology'));
  beforeEach(module('templates'));

  // inject the cartService
  beforeEach(inject(function (_ServiceRelation_) {
    // The injector unwraps the underscores (_) from around the parameter names when matching
    Service = _ServiceRelation_;
  }));

  describe('given a service', () => {

    const levelRelations = [
      {
        subscriber_service: 1
      },
      {
        subscriber_service: 1
      },
      {
        subscriber_service: 2
      }
    ];

    it('should find all involved relations', () => {
      expect(typeof Service.findLevelRelation).toBe('function');
      let levelRelation = Service.findLevelRelation(levelRelations, 1);
      expect(levelRelation.length).toBe(2);
    });
  });

  describe('given a set of relation', () => {

    const levelRelations = [
      {
        provider_service: 1
      },
      {
        provider_service: 2
      }
    ];

    const services = [
      {
        id: 1
      },
      {
        id: 2
      },
      {
        id: 3
      }
    ];

    it('should find all the provider service', () => {
      expect(typeof Service.findLevelServices).toBe('function');
      let levelServices = Service.findLevelServices(levelRelations, services);
      expect(levelServices.length).toBe(2);
    });
  });

  describe('given a list of services and a list of relations', () => {

    const services = [
      {
        id: 1,
        humanReadableName: 'service-1'
      },
      {
        id: 2,
        humanReadableName: 'service-2'
      },
      {
        id: 3,
        humanReadableName: 'service-3'
      },
      {
        id: 4,
        humanReadableName: 'service-4'
      }
    ];

    const relations = [
      {
        provider_service: 2,
        subscriber_service: 1,
      },
      {
        provider_service: 3,
        subscriber_service: 2
      },
      {
        provider_service: 4,
        subscriber_service: 1
      },
      {
        subscriber_root: 1,
        provider_service: 1
      }
    ];

    it('should return a tree ordered by relations', () => {
      let tree = Service.buildServiceTree(services, relations);

      expect(tree.name).toBe('fakeSubs');
      expect(tree.parent).toBeNull();
      expect(tree.children.length).toBe(1);

      expect(tree.children[0].name).toBe('service-1');
      expect(tree.children[0].parent).toBeNull();
      expect(tree.children[0].children.length).toBe(2);

      expect(tree.children[0].children[0].name).toBe('service-2');
      expect(tree.children[0].children[0].children[0].name).toBe('service-3');
      expect(tree.children[0].children[0].children[0].children[0].name).toBe('Internet');

      expect(tree.children[0].children[1].name).toBe('service-4');
      expect(tree.children[0].children[1].children[0].name).toBe('Internet');
    });
  });

  describe('given an object', () => {

    const sample = {
      name: '1',
      children: [
        {
          name: '2',
          children: [
            {
              name: '3'
            }
          ]
        }
      ]
    };

    it('should return the depth', () => {
      expect(Service.depthOf(sample)).toBe(3);
    });
  });


});