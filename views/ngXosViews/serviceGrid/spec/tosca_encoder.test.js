(function () {
  'use strict';
  describe('The Tosca Encoder Service', () => {

    var service, httpBackend, rootScope, ArchiveManagerSpy, toscaBase;

    const serviceData = {
      id: 1,
      name: 'vsg',
      kind: 'vCPE'
    };

    const toscaBaseDefault = {
      topology_template: {
        node_templates: {}
      }
    };

    beforeEach(module('xos.serviceGrid'));
    beforeEach(module('templates'));

    beforeEach(inject(function($httpBackend, $rootScope, ToscaEncoder, ArchiveManager){

      httpBackend = $httpBackend;
      rootScope = $rootScope;
      toscaBase = angular.copy(toscaBaseDefault);
      service = ToscaEncoder;
      ArchiveManagerSpy = ArchiveManager;
      spyOn(ArchiveManagerSpy, 'createArchive');
      spyOn(ArchiveManagerSpy, 'addFile');
      spyOn(ArchiveManagerSpy, 'download');
    }));

    describe('the serviceToTosca method', () => {

      const fakePropertiesDefault = {
        tosca_definitions_version: 'tosca_simple_yaml_1_0',
        description: 'Just enough Tosca to get the vSG slice running on the CORD POD',
        imports: [
          'custom_types/xos.yaml'
        ],
        topology_template:{
          node_templates: {
            'service#vsg': {
              type: 'tosca.nodes.VSGService',
              properties: {
                view_url: 'viewUrl',
                icon_url: 'iconUrl',
                kind: 'vCPE'
              }
            }
          }
        }
      };

      const fakeRequirements = {
        tosca_definitions_version: 'tosca_simple_yaml_1_0',
        description: 'Just enough Tosca to get the vSG slice running on the CORD POD',
        imports: [
          'custom_types/xos.yaml'
        ],
        topology_template:{
          node_templates: {
            'service#vsg': {
              type: 'tosca.nodes.VSGService',
              properties: {
                view_url: 'viewUrl',
                icon_url: 'iconUrl',
                kind: 'vCPE'
              },
              requirements: [
                {
                  node: 'service#vrouter',
                  relationship: 'tosca.relationships.TenantOfService'
                },
                {
                  node: 'service#volt',
                  relationship: 'tosca.relationships.TenantOfService'
                }
              ]
            }
          }
        }
      };

      const expectedWithoutRequirements = `tosca_definitions_version: tosca_simple_yaml_1_0
description: Just enough Tosca to get the vSG slice running on the CORD POD
imports:
  - custom_types/xos.yaml
topology_template:
  node_templates:
    service#vsg:
      type: tosca.nodes.VSGService
      properties:
        view_url: viewUrl
        icon_url: iconUrl
        kind: vCPE
`;

      const expectedWithRequirements = `tosca_definitions_version: tosca_simple_yaml_1_0
description: Just enough Tosca to get the vSG slice running on the CORD POD
imports:
  - custom_types/xos.yaml
topology_template:
  node_templates:
    service#vsg:
      type: tosca.nodes.VSGService
      properties:
        view_url: viewUrl
        icon_url: iconUrl
        kind: vCPE
      requirements:
        - node: service#vrouter
          relationship: tosca.relationships.TenantOfService
        - node: service#volt
          relationship: tosca.relationships.TenantOfService
`;

      const expectedWithSlices = `tosca_definitions_version: tosca_simple_yaml_1_0
description: Just enough Tosca to get the vSG slice running on the CORD POD
imports:
  - custom_types/xos.yaml
topology_template:
  node_templates:
    service#vsg:
      type: tosca.nodes.VSGService
      properties:
        view_url: viewUrl
        icon_url: iconUrl
        kind: vCPE
    service_slice:
      description: A service slice
      type: tosca.nodes.Slice
      properties:
        network: noauto
`;

      let formatPromise, requirementPromise, slicesPromise, fakeProperties, serviceEncoderSpy, slicesEncoderSpy;

      beforeEach(inject(($q, ServiceEncoder, SlicesEncoder) => {

        serviceEncoderSpy = ServiceEncoder;
        slicesEncoderSpy = SlicesEncoder;

        // clone the base property for mock
        fakeProperties = angular.copy(fakePropertiesDefault);

        // create the promises
        // this will be resolved in the single IT block,
        // to allow different resolutions
        formatPromise = $q.defer();
        requirementPromise = $q.defer();
        slicesPromise = $q.defer();

        // mock functions and return promises
        spyOn(serviceEncoderSpy, 'formatServiceProperties').and.callFake(function(){
          return formatPromise.promise;
        });
        spyOn(serviceEncoderSpy, 'getServiceRequirements').and.callFake(function(){
          return requirementPromise.promise;
        });
        spyOn(slicesEncoderSpy, 'getServiceSlices').and.callFake(function(){
          return slicesPromise.promise;
        });
      }));

      it('should create a new archive', () => {
        service.serviceToTosca(serviceData);
        expect(ArchiveManagerSpy.createArchive).toHaveBeenCalled();
      });

      it('should add the service file to the archive', (done) => {
        service.serviceToTosca(serviceData)
        .then(() => {
          expect(ArchiveManagerSpy.addFile).toHaveBeenCalledWith('vsg_service.yaml', expectedWithoutRequirements);
          expect(ArchiveManagerSpy.download).toHaveBeenCalledWith('vsg');
          done();
        });
        formatPromise.resolve(fakeProperties);
        requirementPromise.resolve(fakeProperties);
        slicesPromise.resolve(fakeProperties);
        rootScope.$apply();
      });

      // IS IT REALLY USEFULL TO TEST THE CONVERTION TO YAML?
      xit('should create a tosca spec with no requirements', (done) => {
        service.serviceToTosca(serviceData)
          .then(res => {
            expect(res).toEqual(expectedWithoutRequirements);
            done();
          });
        formatPromise.resolve(fakeProperties);
        requirementPromise.resolve(fakeProperties);
        slicesPromise.resolve(fakeProperties);
        rootScope.$apply();
      });

      xit('should create a tosca spec with requirements', (done) => {
        service.serviceToTosca(serviceData)
          .then(res => {
            expect(res).toEqual(expectedWithRequirements);
            done();
          });
        formatPromise.resolve(fakeProperties);
        requirementPromise.resolve(fakeRequirements);
        slicesPromise.resolve(fakeProperties);
        rootScope.$apply();
      });

      xit('should create a tosca spec with additional slices', (done) => {

        // this is dirty, we are changing an object and shouldn't be done in tests
        angular.extend(
          fakeProperties.topology_template.node_templates, {service_slice: {
            description: 'A service slice',
            type: 'tosca.nodes.Slice',
            properties: {
              network: 'noauto'
            }
          }});

        service.serviceToTosca(serviceData)
          .then(res => {
            expect(res).toEqual(expectedWithSlices);
            done();
          });
        formatPromise.resolve(fakeProperties);
        requirementPromise.resolve(fakeProperties);
        slicesPromise.resolve(fakeProperties);
        rootScope.$apply();
      });
    });
  });
}());