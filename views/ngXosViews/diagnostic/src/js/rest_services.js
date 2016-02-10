(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .service('Services', function($resource){
    return $resource('/xos/services/:id', {id: '@id'});
  })
  .service('Tenant', function($resource){
    return $resource('/xos/tenants');
  })
  .service('Slice', function($resource){
    return $resource('/xos/slices', {id: '@id'});
  })
  .service('Instances', function($resource){
    return $resource('/xos/instances', {id: '@id'});
  })
  .service('Subscribers', function($resource, $q, SubscriberDevice){
    return $resource('/xos/subscribers', {id: '@id'}, {
      queryWithDevices: {
        method: 'GET',
        isArray: true,
        interceptor: {
          response: function(res){

            /**
            * For each subscriber retrieve devices and append them
            */

            const deferred = $q.defer();

            let requests = [];

            angular.forEach(res.data, (subscriber) => {
              requests.push(SubscriberDevice.query({id: subscriber.id}).$promise);
            })

            $q.all(requests)
            .then((list) => {
              res.data.map((subscriber, i) => {
                subscriber.devices = list[i];
                subscriber.type = 'subscriber';

                subscriber.devices.map(d => d.type = 'device')

                return subscriber;
              });

              // faking to have 2 subscriber
              res.data.push(angular.copy(res.data[0]));

              deferred.resolve(res.data);
            })

            return deferred.promise;
          }
        }
      }
    });
  })
  .service('SubscriberDevice', function($resource){
    return $resource('/xoslib/rs/subscriber/:id/users/', {id: '@id'});
  })
  .service('ServiceRelation', function($q, lodash, Services, Tenant, Slice, Instances){

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
      return lodash.filter(tenants, service => {
        return service.subscriber_service === rootId;
      });
    };

    const findSpecificInformation = (tenants, rootId) => {
      var tenants = lodash.filter(tenants, service => {
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
      lodash.forEach(relations, (tenant) => {
        var service = lodash.find(services, {id: tenant.provider_service});
        levelServices.push(service);
      });
      return levelServices;
    };

    const buildLevel = (tenants, services, rootService, parentName = null) => {

      // build an array of unlinked services
      // these are the services that should still placed in the tree
      var unlinkedServices = lodash.difference(services, [rootService]);

      // find all relations relative to this rootElement
      const levelRelation = findLevelRelation(tenants, rootService.id);

      // find all items related to rootElement
      const levelServices = findLevelServices(levelRelation, services);

      // remove this item from the list (performance
      unlinkedServices = lodash.difference(unlinkedServices, levelServices);

      rootService.service_specific_attribute = findSpecificInformation(tenants, rootService.id);

      const tree = {
        name: rootService.humanReadableName,
        parent: parentName,
        type: 'service',
        service: rootService,
        children: []
      };

      lodash.forEach(levelServices, (service) => {
        tree.children.push(buildLevel(tenants, unlinkedServices, service, rootService.humanReadableName));
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

    const buildServiceTree = (services, tenants, subscriber = {id: 1, name: 'fakeSubs'}) => {

      // find the root service
      // it is the one attached to subsriber_root
      // as now we have only one root so this can work
      const rootServiceId = lodash.find(tenants, {subscriber_root: subscriber.id}).provider_service;
      const rootService = lodash.find(services, {id: rootServiceId});

      const serviceTree = buildLevel(tenants, services, rootService);

      return {
        name: subscriber.name,
        parent: null,
        type: 'subscriber',
        children: [serviceTree]
      };

    };

    const get = (subscriber) => {
      var deferred = $q.defer();
      var services, tenants;
      Services.query().$promise
      .then((res) => {
        services = res;
        return Tenant.query().$promise;
      })
      .then((res) => {
        tenants = res;
        deferred.resolve(buildServiceTree(services, tenants, subscriber));
      })
      .catch((e) => {
        throw new Error(e);
      });

      return deferred.promise;
    };

    // export APIs
    return {
      get: get,
      buildLevel: buildLevel,
      buildServiceTree: buildServiceTree,
      findLevelRelation: findLevelRelation,
      findLevelServices: findLevelServices,
      depthOf: depthOf,
      findSpecificInformation: findSpecificInformation
    }
  });

}());