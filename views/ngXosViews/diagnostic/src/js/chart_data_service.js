(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .service('ChartData', function($rootScope, $q, lodash, Tenant, Node, serviceTopologyConfig, Ceilometer) {
    this.currentSubscriber = null;
    this.currentServiceChain = null;

    this.logicTopologyData = {
      name: 'Router',
      type: 'router',
      children: [
        {
          name: 'WAN',
          type: 'network',
          children: [
            {
              name: 'Rack',
              type: 'rack',
              computeNodes: [],
              children: [
                {
                  name: 'LAN',
                  type: 'network',
                  children: [{
                    name: 'Subscriber',
                    type: 'subscriber'
                  }] //subscribers goes here
                }
              ]
            }
          ]
        }
      ]
    };

    this.getLogicTree = () => {
      const deferred = $q.defer();

      Node.queryWithInstances().$promise
        .then((computeNodes) => {
          this.logicTopologyData.children[0].children[0].computeNodes = computeNodes;
          // LogicTopologyHelper.updateTree(svg);
          deferred.resolve(this.logicTopologyData);
        });

      return deferred.promise;
    };

    /**
    * Add Subscriber tag to LAN Network
    */
    this.addSubscriberTag = (tags) => {
      this.logicTopologyData.children[0].children[0].children[0].subscriberTag = {
        cTag: tags.c_tag,
        sTag: tags.s_tag
      }
    };

    /**
    * Add Subscribers to the tree
    */
    this.addSubscriber = (subscriber) => {
      subscriber.children = subscriber.devices;

      // add subscriber to data tree
      this.logicTopologyData.children[0].children[0].children[0].children = [subscriber];
      return this.logicTopologyData;
    };

    this.getSubscriberTag = () => {

      this.addSubscriberTag(JSON.parse(this.currentServiceChain.children[0].tenant.service_specific_attribute));

    };

    this.getSubscriberIP = () => {
      const ip = this.currentServiceChain.children[0].children[0].tenant.wan_container_ip;
      this.logicTopologyData.children[0].subscriberIP = ip;
    };

    this.selectSubscriber = (subscriber) => {

      // append the device with to config settings
      serviceTopologyConfig.elWidths.push(160);

      this.addSubscriber(angular.copy(subscriber));

      this.getSubscriberTag();
      this.getSubscriberIP();

    };

    this.highlightInstances = (instances) => {

      const computeNodes = this.logicTopologyData.children[0].children[0].computeNodes;

      // unselect all
      computeNodes.map((node) => {
        node.instances.map((instance) => {
          instance.selected = false
          return instance;
        });
      });

      lodash.forEach(instances, (instance) => {
        computeNodes.map((node) => {
          node.instances.map((d3instance) => {
            if(d3instance.id === instance.id){
              d3instance.selected = true;
            }
            return d3instance;
          });
        });
      });

    }

    this.getInstanceStatus = (service) => {
      const deferred = $q.defer();

      // NOTE consider if subscriber is selected or not,
      // if not select instances
      // else select containers (and follow subscriber chain to find the correct instance)

      let p;

      if(this.currentSubscriber){
        let instances = [JSON.parse(service.tenant.service_specific_attribute).instance_id];
        p = Ceilometer.getInstancesStats(instances);
      }
      else {
        let param = {
          'service_vsg': {kind: 'vCPE'},
          'service_vbng': {kind: 'vBNG'},
          'service_volt': {kind: 'vOLT'}
        };

        p = Tenant.queryVsgInstances(param[service.name]).$promise
        .then((instances) => {

          return Ceilometer.getInstancesStats(instances);
        });
      }

      p.then((instances) => {
        this.highlightInstances(instances);
        deferred.resolve(instances);
      })
      .catch((e) => {
        deferred.reject(e);
      });

      return deferred.promise;
    };
  })
})();
