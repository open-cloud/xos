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
  .service('Subscribers', function($resource){
    return $resource('/xos/subscribers', {id: '@id'});
  })
  .service('ServiceRelation', function($q, _, lodash, Services, Tenant){

    // find all the relation defined for a given root
    const findLevelRelation = (tenants, rootId) => {
      return lodash.filter(tenants, service => {
        return service.subscriber_service === rootId;
      });
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

      const tree = {
        name: rootService.humanReadableName,
        parent: parentName,
        service: rootService,
        children: []
      };

      // build an array of unlinked services
      // these are the services that should still placed in the tree
      var unlinkedServices = lodash.difference(services, [rootService]);

      // find all relations relative to this rootElement
      const levelRelation = findLevelRelation(tenants, rootService.id);

      // find all items related to rootElement
      const levelServices = findLevelServices(levelRelation, services);

      // remove this item from the list (performance
      unlinkedServices = lodash.difference(unlinkedServices, levelServices);

      lodash.forEach(levelServices, (service) => {
        tree.children.push(buildLevel(tenants, unlinkedServices, service, rootService.humanReadableName));
      });

      return tree;
    };

    const buildServiceTree = (services, tenants, subscriber = {id:1, name: 'fakeSubs'}) => {

      // find the root service
      // it is the one attached to subsriber_root
      // as now we have only one root so this can work
      const rootServiceId = lodash.find(tenants, {subscriber_root: subscriber.id}).provider_service;
      const rootService = lodash.find(services, {id: rootServiceId});

      const serviceTree = buildLevel(tenants, services, rootService);

      return {
        name: subscriber.name,
        parent: null,
        children: [serviceTree]
      };

      //return serviceTree;
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
    }

    this.get = get;
    this.buildLevel = buildLevel;
    this.buildServiceTree = buildServiceTree;
    this.findLevelRelation = findLevelRelation;
    this.findLevelServices = findLevelServices;
  });

}());