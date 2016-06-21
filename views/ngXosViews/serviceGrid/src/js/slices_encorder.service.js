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
   * @name xos.SlicesEncoder.serviceGrid
   **/

  angular.module('xos.serviceGrid')
  .service('SlicesEncoder', function($q, _, Slices, SiteEncoder, ImageEncoder, NetworkEncoder){

    this.buildTosca = (slices, toscaSpec, serviceName) => {
      // store here the promise that will build the dependency structure
      let dependency = {};

      const d = $q.defer();
      slices = _.reduce(slices, (obj, s) => {
        obj[s.name] = {
          type: 'tosca.nodes.Slice',
          properties: {
            network: s.network
          },
          requirements: [
            // by default slices are connected to management network
            {
              management: {
                node: 'management',
                relationship: 'tosca.relationships.ConnectsToNetwork'
              }
            },
          ]
        };

        if(angular.isDefined(serviceName)){
          let service = {};
          service[`${serviceName}_service`] = {
            node: `service#${serviceName}`,
            relationship: 'tosca.relationships.MemberOfService'
          };
          obj[s.name].requirements.push(service);
        }

        if(angular.isDefined(s.description)){
          obj[s.name].description = s.description;
        }
        
        if(angular.isDefined(s.site)){
          dependency[`${s.name}#site`] = SiteEncoder.buildTosca(s.site, toscaSpec);
        }
        if(angular.isDefined(s.default_image)){
          dependency[`${s.name}#image`] = ImageEncoder.buildTosca(s.default_image, toscaSpec);
        }
        if(angular.isDefined(s.networks) && s.networks.length > 0){
          dependency[`${s.name}#management`] = NetworkEncoder.getSliceNetworks(s, toscaSpec);
        }

        return obj;
      }, {});

      // if we have dependency wait for them
      if(Object.keys(dependency).length > 0){

        let relationMap = {
          site: 'tosca.relationships.MemberOfSite',
          image: 'tosca.relationships.DefaultImage'
        };

        // NOTE create a reference to the management network
        toscaSpec.topology_template.node_templates['management'] = {
          type: 'tosca.nodes.network.Network.XOS',
          properties: {
            'no-create': true,
            'no-delete': true,
            'no-update': true
          }
        };

        $q.all(dependency)
        .then(deps => {

          for(let k of Object.keys(deps)){

            // this is UGLY!!!
            // we are passing the requirement type inside the object key
            // in which the promise is stored.
            // This let us build the requirements array
            let [sliceName, requirementType] = k.split('#');

            if(angular.isDefined(relationMap[requirementType])){

              if(!slices[sliceName].requirements){
                slices[sliceName].requirements = [];
              }

              let [tosca, resource] = deps[k];

              let requirementObj = {};

              let reqName;

              // NOTE site have problem with prefixing
              if(requirementType === 'site'){
                reqName = resource.name;
              }
              else{
                reqName = `${requirementType}#${resource.name}`;
              }

              requirementObj[requirementType] = {
                node: reqName,
                relationship: relationMap[requirementType]
              };

              slices[sliceName].requirements.push(requirementObj);

              angular.extend(toscaSpec, tosca);
            }

          }
          // here we add slices to tosca
          angular.extend(toscaSpec.topology_template.node_templates, slices);
          d.resolve(toscaSpec);
        })
        .catch(e => {
          throw new Error(e);
        });
      }
      //else resolve directly
      else {
        angular.extend(toscaSpec.topology_template.node_templates, slices);
        d.resolve(toscaSpec);
      }

      return d.promise;
    };

    this.getServiceSlices = (service, toscaSpec) => {
      const d = $q.defer();
      Slices.query({service: service.id}).$promise
      .then(slices => {
        return this.buildTosca(slices, toscaSpec, service.name)
      })
      .then(slicesTosca => {
        d.resolve(slicesTosca);
      });

      return d.promise;
    };
  });
})();

