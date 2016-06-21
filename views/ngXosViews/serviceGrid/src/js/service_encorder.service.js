/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 6/22/16.
 */

(function () {
  'use strict';

  /**
   * @ngdoc service
   * @name xos.toscaExporter.serviceGrid
   **/

  angular.module('xos.serviceGrid')
    .service('ServiceEncoder', function($q, ArchiveManager, Tenants, Services){

      const serviceTypes = {
        fabric: 'tosca.nodes.FabricService',
        onos: 'tosca.nodes.ONOSService',
        vCPE: 'tosca.nodes.VSGService',
        vOLT: 'tosca.nodes.VOLTService',
        vROUTER: 'tosca.nodes.VRouterService',
        VTN: 'tosca.nodes.VTNService',
        vTR: 'tosca.nodes.Service'
      };

      this.formatServiceProperties = (service, toscaSpec) => {
        const d = $q.defer();
        const serviceName = `service#${service.name}`;
        // create the structure to hold the service
        toscaSpec.topology_template.node_templates[serviceName] = {};
        toscaSpec.topology_template.node_templates[serviceName].type = serviceTypes[service.kind] || 'tosca.nodes.Service';

        const res = {
          properties: {
            kind: service.kind
          }
        };

        if(angular.isDefined(service.view_url)){
          res.properties.view_url = service.view_url;
        }

        if(angular.isDefined(service.icon_url)){
          res.properties.icon_url = service.icon_url;
        }

        if(angular.isDefined(service.private_key_fn)){
          res.properties.private_key_fn = service.private_key_fn;
        }

        if(angular.isDefined(service.public_key)){
          ArchiveManager.addFile(`${service.name}_rsa.pub`, service.public_key);
          res.properties.public_key = '{ get_artifact: [ SELF, pubkey, LOCAL_FILE] }'
          res['artifacts'] = {
            pubkey: `/opt/xos/tosca/${service.name}/${service.name}_rsa.pub`
          };
          toscaSpec.topology_template.node_templates[serviceName].artifacts = res.artifacts;
        }

        toscaSpec.topology_template.node_templates[serviceName].properties = res.properties;
        d.resolve(toscaSpec);
        return d.promise;
      };

      this.getServiceRequirements = (service, toscaSpec) => {
        const d = $q.defer();

        Tenants.query({subscriber_service: service.id}).$promise
          .then(tenants => {
            const services = [];
            // avoid multiple request for the same service
            tenants = _.uniqBy(tenants, 'provider_service');

            _.forEach(tenants, t => {
              services.push(Services.get({id: t.provider_service}).$promise);
            });

            return $q.all(services)
          })
          .then((deps) => {
            // Get the provider service and create an array of unique names
            let requirements = _.reduce(deps, (list, d) => list.concat(d.name), []);

            // create a object for requirements, later will parsed in Yaml
            requirements = _.reduce(requirements, (list, r) => {
              let name = `${r}_tenant`;
              let obj = {};
              obj[name] = {
                node: `service#${r}`,
                relationship: 'tosca.relationships.TenantOfService'
              };
              return list.concat(obj);
            }, []);

            if(requirements.length > 0){

              // NOTE set a reference to the requirements in tosca
              _.forEach(requirements, r => {
                let reqName = r[Object.keys(r)[0]].node;
                toscaSpec.topology_template.node_templates[reqName] = {
                  type: 'tosca.nodes.Service',
                  properties: {
                    'no-create': true,
                    'no-delete': true,
                    'no-update': true
                  }
                };
              });

              const serviceName = `service#${service.name}`;
              toscaSpec.topology_template.node_templates[serviceName].requirements = requirements;
            }

            d.resolve(toscaSpec);
          });

        return d.promise;
      };
    });
})();

