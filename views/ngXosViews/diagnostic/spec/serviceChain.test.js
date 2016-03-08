'use strict';

describe('The Service Relation Service', () => {
  
  var Service;

  beforeEach(module('xos.diagnostic'));
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
        provider_service: 1,
        service_specific_attribute: '{"instance_id": "instance1"}',
        subscriber_tenant: 2
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

    it('should retrieve all service specific information', () => {
      let info = Service.findSpecificInformation(levelRelations, 1);
      expect(info.instance_id).toBe('instance1');
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

    const tenants = [
      {
        id: 1,
        provider_service: 2,
        subscriber_tenant: 4,
        subscriber_service: 1,
      },
      {
        id: 2,
        provider_service: 3,
        subscriber_tenant: 1,
        subscriber_service: 2
      },
      {
        id: 3,
        provider_service: 4,
        subscriber_tenant: 4,
        subscriber_service: 1
      },
      {
        id: 4,
        subscriber_root: 1,
        provider_service: 1
      }
    ];

    it('should return a tree ordered by tenants', () => {
      let tree = Service.buildSubscriberServiceTree(services, tenants);

      expect(tree.name).toBe('fakeSubs');
      expect(tree.parent).toBeNull();
      expect(tree.children.length).toBe(1);

      expect(tree.children[0].name).toBe('service-1');
      expect(tree.children[0].parent).toBeNull();
      expect(tree.children[0].tenant).toEqual({id: 4, subscriber_root: 1, provider_service: 1});
      expect(tree.children[0].children.length).toBe(2);

      expect(tree.children[0].children[0].name).toBe('service-2');
      expect(tree.children[0].children[0].tenant).toEqual({ id: 1, provider_service: 2, subscriber_tenant: 4, subscriber_service: 1 });;
      expect(tree.children[0].children[0].children[0].name).toBe('service-3');

      // expect(tree.children[0].children[0].children[0].children[0].name).toBe('Router');

      expect(tree.children[0].children[1].name).toBe('service-4');
      // expect(tree.children[0].children[1].children[0].name).toBe('Router');
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

  describe('Given a list of services and COARSE tenant', () => {
    
    const coarseTenants = [
      {
        humanReadableName: 'coarse-1',
        provider_service: 1,
        subscriber_service: 2
      },
      {
        humanReadableName: 'coarse-2',
        provider_service: 2,
        subscriber_service: 3
      }
    ];

    const services = [
      {
        id: 1,
        name: 'vbng',
        humanReadableName: 'vbng'
      },
      {
        id: 2,
        name: 'vsg',
        humanReadableName: 'vsg'
      },
      {
        id: 3,
        name: 'volt',
        humanReadableName: 'volt'
      }
    ];

    it('should build the tenancy graph', () => {
      let tree = Service.buildServiceTree(services, coarseTenants);

      expect(tree.type).toBe('subscriber');
      expect(tree.children[0].name).toBe('volt');
      expect(tree.children[0].service).toBeDefined();
      expect(tree.children[0].children[0].name).toBe('vsg');
      expect(tree.children[0].children[0].children[0].name).toBe('vbng');
    });
  });

});