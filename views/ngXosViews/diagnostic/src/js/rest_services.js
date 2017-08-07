
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


(function () {
  'use strict';

  angular.module('xos.diagnostic')
  .service('Services', function($resource){
    return $resource('/api/core/services/:id', {id: '@id'});
  })
  .service('Tenant', function($resource){
    return $resource('/api/core/tenants', {id: '@id'}, {
      queryVsgInstances: {
        method: 'GET',
        isArray: true,
        interceptor: {
          response: (res) => {

            // NOTE
            // Note that VCPETenant is now VSGTenant.

            let instances = [];

            angular.forEach(res.data, (tenant) => {
              let info = JSON.parse(tenant.service_specific_attribute);
              if(info && info.instance_id){
                instances.push(info.instance_id);
              }
            });

            return instances;
          }
        }
      },
      getSubscriberTag: {
        method: 'GET',
        isArray: true,
        interceptor: {
          response: (res) => {
            // NOTE we should receive only one vOLT tenant here
            return JSON.parse(res.data[0].service_specific_attribute);
          }
        }
      }
    });
  })
  .service('Ceilometer', function($http, $q, Instances) {

    /**
    * Get stats for a single instance
    */
    this.getInstanceStats = (instanceUuid) => {
      let deferred = $q.defer();

      $http.get('/xoslib/xos-instance-statistics', {params: {'instance-uuid': instanceUuid}})
      .then((res) => {
        deferred.resolve(res.data);
      })
      .catch((e) => {
        deferred.reject(e);
      })

      return deferred.promise;
    };

    /**
    * Collect stats for an array of instances
    */
    this.getInstancesStats = (instances) => {
      let deferred = $q.defer();
      let instancePromises = [];
      let instanceList = [];

      // retrieve instance details
      instances.forEach((instanceId) => {
        instancePromises.push(Instances.get({id: instanceId}).$promise);
      });

      // get all instance data
      $q.all(instancePromises)
      .then((_instanceList) => {
        instanceList = _instanceList;
        let promises = [];
        // foreach instance query stats
        instanceList.forEach((instance) => {
          promises.push(this.getInstanceStats(instance.instance_uuid));
        });
        return $q.all(promises);
      })
      .then(stats => {
        // augment instance with stats information
        instanceList.map((instance, i) => {
          instance.stats = stats[i];
        });
        deferred.resolve(instanceList);
      })
      .catch(deferred.reject);

      return deferred.promise;
    };

    this.getContainerStats = (containerName) => {
      const deferred = $q.defer();

      let res = {};

      $http.get('/xoslib/meterstatistics', {params: {'resource': containerName}})
      .then((containerStats) => {
        res.stats = containerStats.data;
        return $http.get('/xoslib/meterstatistics', {params: {'resource': `${containerName}-eth0`}})
      })
      .then((portStats) => {
        res.port = {
          eth0: portStats.data
        };
        return $http.get('/xoslib/meterstatistics', {params: {'resource': `${containerName}-eth1`}})
      })
      .then((portStats) => {
        res.port.eth1 = portStats.data;
        deferred.resolve(res);
      })
      .catch((e) => {
        deferred.reject(e);
      })

      return deferred.promise;
    }
  })
  .service('Slice', function($resource){
    return $resource('/api/core/slices', {id: '@id'});
  })
  .service('Instances', function($resource){
    return $resource('/api/core/instances/:id', {id: '@id'});
  })
  .service('Node', function($resource, $q, Instances){
    return $resource('/api/core/nodes', {id: '@id'}, {
      queryWithInstances: {
        method: 'GET',
        isArray: true,
        interceptor: {
          response: function(res){

            // TODO update the API to include instances in nodes
            // http://stackoverflow.com/questions/14573102/how-do-i-include-related-model-fields-using-django-rest-framework

            const deferred = $q.defer();

            let requests = [];

            angular.forEach(res.data, (node) => {
              requests.push(Instances.query({node: node.id}).$promise);
            })

            $q.all(requests)
            .then((list) => {
              res.data.map((node, i) => {
                node.instances = list[i];
                return node;
              });
              deferred.resolve(res.data);
            })

            return deferred.promise;
          }
        }
      }
    });
  })
  // TODO extend the resource in xosLib
  .service('SubscribersWithDevice', function($http, $q, Subscribers){

    this.get = (s) => {
      const d = $q.defer();
      let subscriber;

      Subscribers.get({id: s.id}).$promise
      .then(res => {
        subscriber = res;
        return $http.get(`/api/tenant/cord/subscriber/${subscriber.id}/devices/`);
      })
      .then(res => {
        res.data.map(d => d.type = 'device');
        subscriber.devices = res.data;
        subscriber.type = 'subscriber';
        d.resolve(subscriber);
      })
      .catch(err => {
        d.reject(err);
      });
      return {$promise: d.promise};
    };

  })
  .service('ServiceRelation', function($q, _, Services, Tenant, Slice, Instances){

    // count the mas depth of an object
    const depthOf = (obj) => {
      var depth = 0;
      if (obj.children) {
        obj.children.forEach(function (d) {
          var tmpDepth = depthOf(d);
          if (tmpDepth > depth) {
            depth = tmpDepth
          }
        })
      }
      return 1 + depth
    };

    // find all the relation defined for a given root
    const findLevelRelation = (tenants, rootId) => {
      return _.filter(tenants, service => {
        return service.subscriber_service === rootId;
      });
    };

    const findSpecificInformation = (tenants, rootId) => {
      var tenants = _.filter(tenants, service => {
        return service.provider_service === rootId && service.subscriber_tenant;
      });

      var info;

      tenants.forEach((tenant) => {
        if(tenant.service_specific_attribute){
          info = JSON.parse(tenant.service_specific_attribute);
        }
      });

      return info;
    };

    // find all the service defined by a given array of relations
    const findLevelServices = (relations, services) => {
      const levelServices = [];
      _.forEach(relations, (tenant) => {
        var service = _.find(services, {id: tenant.provider_service});
        levelServices.push(service);
      });
      return levelServices;
    };

    const buildLevel = (tenants, services, rootService, rootTenant, parentName = null) => {

      // build an array of unlinked services
      // these are the services that should still placed in the tree
      var unlinkedServices = _.difference(services, [rootService]);

      // find all relations relative to this rootElement
      const levelRelation = findLevelRelation(tenants, rootService.id);
      // find all items related to rootElement
      const levelServices = findLevelServices(levelRelation, services);

      // remove this item from the list (performance
      unlinkedServices = _.difference(unlinkedServices, levelServices);

      rootService.service_specific_attribute = findSpecificInformation(tenants, rootService.id);

      if(rootService.humanReadableName === 'service_vbng'){
        rootService.humanReadableName = 'service_vrouter'
      }

      const tree = {
        name: rootService.humanReadableName,
        parent: parentName,
        type: 'service',
        service: rootService,
        tenant: rootTenant,
        children: []
      };

      _.forEach(levelServices, (service) => {
        if(service.humanReadableName === 'service_ONOS_vBNG' || service.humanReadableName === 'service_ONOS_vOLT'){
          // remove ONOSes from service chart
          return;
        }
        let tenant = _.find(tenants, {subscriber_tenant: rootTenant.id, provider_service: service.id});
        tree.children.push(buildLevel(tenants, unlinkedServices, service, tenant, rootService.humanReadableName));
      });

      // if it is the last element append internet
      if(tree.children.length === 0){
        tree.children.push({
          name: 'Router',
          type: 'router',
          children: []
        });
      }

      return tree;
    };

    const buildSubscriberServiceTree = (services, tenants, subscriber = {id: 1, name: 'fakeSubs'}) => {

      // find the root service
      // it is the one attached to subsriber_root
      // as now we have only one root so this can work
      const rootTenant = _.find(tenants, {subscriber_root: subscriber.id});
      const rootService = _.find(services, {id: rootTenant.provider_service});

      const serviceTree = buildLevel(tenants, services, rootService, rootTenant);

      return {
        name: subscriber.name || subscriber.humanReadableName,
        parent: null,
        type: 'subscriber',
        children: [serviceTree]
      };

    };

    // applying domain knowledge to build the global service tree
    const buildServiceTree = (services, tenants) => {

      // TODO refactor
      const buildChild = (services, tenants, currentService) => {

        if(currentService.humanReadableName === 'service_vbng'){
          currentService.humanReadableName = 'service_vrouter'
        }

        const response = {
          type: 'service',
          name: currentService.humanReadableName,
          service: currentService
        };

        let tenant = _.find(tenants, {subscriber_service: currentService.id});
        if(tenant){
          let next = _.find(services, {id: tenant.provider_service});
          response.children = [buildChild(services, tenants, next)];
        }
        else {
          response.children = [
            {
              name: 'Router',
              type: 'router',
              children: []
            }
          ]
        }
        delete currentService.id; // conflict with d3
        return response;
      }

      let baseService = _.find(services, {id: 3});
      
      if(!angular.isDefined(baseService)){
        console.error('Missing Base service!');
        return;
      }

      const baseData = {
        name: 'Subscriber',
        type: 'subscriber',
        parent: null,
        children: [buildChild(services, tenants, baseService)]
      };
      return baseData;
    };

    const getBySubscriber = (subscriber) => {
      var deferred = $q.defer();
      var services, tenants;
      Services.query().$promise
      .then((res) => {
        services = res;
        return Tenant.query().$promise;
      })
      .then((res) => {
        tenants = res;
        deferred.resolve(buildSubscriberServiceTree(services, tenants, subscriber));
      })
      .catch((e) => {
        throw new Error(e);
      });

      return deferred.promise;
    };

    const get = () => {
      var deferred = $q.defer();
      var services, tenants;
      Services.query().$promise
      .then((res) => {
        services = res;
        return Tenant.query({kind: 'coarse'}).$promise;
      })
      .then((res) => {
        tenants = res;
        deferred.resolve(buildServiceTree(services, tenants));
      })
      .catch((e) => {
        throw new Error(e);
      });

      return deferred.promise;
    }

    // export APIs
    return {
      get: get,
      buildServiceTree: buildServiceTree,
      getBySubscriber: getBySubscriber,
      buildLevel: buildLevel,
      buildSubscriberServiceTree: buildSubscriberServiceTree,
      findLevelRelation: findLevelRelation,
      findLevelServices: findLevelServices,
      depthOf: depthOf,
      findSpecificInformation: findSpecificInformation
    }
  });

}());