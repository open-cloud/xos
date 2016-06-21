/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 6/22/16.
 */

(function () {
  'use strict';
  describe('The Services Encoder Service', () => {

    var service, rootScope, ArchiveManagerSpy, toscaBase;

    const toscaBaseDefault = {
      topology_template: {
        node_templates: {}
      }
    };

    beforeEach(module('xos.serviceGrid'));
    beforeEach(module('templates'));

    beforeEach(inject(($rootScope, ArchiveManager, ServiceEncoder) => {
      rootScope = $rootScope;
      toscaBase = angular.copy(toscaBaseDefault);

      ArchiveManagerSpy = ArchiveManager;
      spyOn(ArchiveManagerSpy, 'createArchive');
      spyOn(ArchiveManagerSpy, 'addFile');
      service = ServiceEncoder;
    }));

    describe('the formatServiceProperties method', () => {

      it('should return only the existing properties', (done) => {
        service.formatServiceProperties({name: 'test', kind: 'vCPE'}, toscaBase)
        .then(res => {
          expect(res).toEqual({
            topology_template:{
              node_templates: {
                'service#test': {
                  type: 'tosca.nodes.VSGService',
                  properties: {kind: 'vCPE'}
                }
              }
            }
          });
          done();
        });
        rootScope.$apply();
      });

      it('should return all properties', (done) => {
        service.formatServiceProperties({
            name: 'test',
            kind: 'vCPE',
            view_url: 'view_url',
            icon_url: 'icon_url',
            private_key_fn: 'private_key_fn'
          }, toscaBase)
          .then(res => {
            expect(res).toEqual({
              topology_template:{
                node_templates: {
                  'service#test': {
                    type: 'tosca.nodes.VSGService',
                    properties: {
                      kind: 'vCPE',
                      view_url: 'view_url',
                      icon_url: 'icon_url',
                      private_key_fn: 'private_key_fn'
                    }
                  }
                }
              }
            });
            done();
          });
        rootScope.$apply();
      });

      describe('when a public key is provided', () => {
        it('should add public_key and artifacts properties', (done) => {

          let expected = {
            topology_template:{
              node_templates: {
                'service#test': {
                  type: 'tosca.nodes.VSGService',
                  properties: {
                    kind: 'vCPE',
                    public_key: '{ get_artifact: [ SELF, pubkey, LOCAL_FILE] }'
                  },
                  artifacts: {
                    pubkey: '/opt/xos/tosca/test/test_rsa.pub'
                  }
                }
              }
            }
          };

          service.formatServiceProperties({
              kind: 'vCPE',
              public_key: 'pkey',
              name: 'test'
            }, toscaBase)
            .then(res => {
              expect(res).toEqual(expected);
              done();
            });
          rootScope.$apply();
        });

        it('should add public_key file to the archive', (done) => {
          service.formatServiceProperties({
              kind: 'vCPE',
              public_key: 'pkey',
              name: 'test'
            }, toscaBase)
            .then(res => {
              expect(ArchiveManagerSpy.addFile).toHaveBeenCalledWith('test_rsa.pub', 'pkey');
              done();
            });
          rootScope.$apply();
        });
      });
    });

    describe('the getServiceRequirements method', () => {
      let TenantSpy, ServiceSpy, tenantQueryPromise;
      beforeEach(inject(function(Tenants, Services, $q){

        tenantQueryPromise= $q.defer();

        TenantSpy = Tenants;
        spyOn(TenantSpy, 'query').and.callFake(function(){
          return {$promise: tenantQueryPromise.promise};
        });

        ServiceSpy = Services;
        spyOn(ServiceSpy, 'get').and.callFake(function(p){
          let d = $q.defer();
          d.resolve({name: `deps_${p.id}`});
          return {$promise: d.promise};
        });
      }));

      it('should call the tenants service with correct params', () => {
        service.getServiceRequirements({id: 1});
        expect(TenantSpy.query).toHaveBeenCalledWith({subscriber_service: 1});
      });

      it('should not add requirements if the current service has no dependency', (done) => {
        service.getServiceRequirements({id: 1}, {})
          .then(res => {
            expect(res).toEqual({});
            done();
          });
        tenantQueryPromise.resolve();
        rootScope.$apply();
      });

      it('should return a list of required service', () => {
        service.getServiceRequirements({id: 1, name: 'test'}, {topology_template: {node_templates: {'service#test': {}}}})
          .then(res => {
            expect(res.topology_template.node_templates['service#test'].requirements).toEqual([
              {
                deps_3_tenant: {
                  node: 'service#deps_3',
                  relationship: 'tosca.relationships.TenantOfService'
                }
              },
              {
                deps_4_tenant: {
                  node: 'service#deps_4',
                  relationship: 'tosca.relationships.TenantOfService'
                }
              }
            ]);
          });
        tenantQueryPromise.resolve([
          {
            subscriber_service: 1,
            provider_service: 3
          },
          {
            subscriber_service: 1,
            provider_service: 4
          }
        ]);
        rootScope.$apply();
      });

      it('should return a list of unique required service', () => {
        service.getServiceRequirements({id: 1, name: 'test'}, {topology_template: {node_templates: {'service#test': {}}}})
          .then(res => {
            expect(res.topology_template.node_templates['service#test'].requirements).toEqual([
              {
                deps_3_tenant: {
                  node: 'service#deps_3',
                  relationship: 'tosca.relationships.TenantOfService'
                }
              }
            ]);
          });
        tenantQueryPromise.resolve([
          {
            subscriber_service: 1,
            provider_service: 3
          },
          {
            subscriber_service: 1,
            provider_service: 3
          }
        ]);
        rootScope.$apply();
      });
    });
  });

})();

