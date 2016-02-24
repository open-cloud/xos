(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .service('ChartData', function($rootScope, $q, lodash, Tenant, Node, serviceTopologyConfig, Ceilometer, Instances) {
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
      };
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
      const tags = JSON.parse(this.currentServiceChain.children[0].tenant.service_specific_attribute);
      delete tags.creator_id;
      
      this.addSubscriberTag(tags);
      // add tags info to current subscriber
      this.currentSubscriber.tags = {
        cTag: tags.c_tag,
        sTag: tags.s_tag
      };

    };

    this.getSubscriberIP = () => {
      const ip = JSON.parse(this.currentServiceChain.children[0].children[0].tenant.service_specific_attribute).wan_container_ip;
      // const ip = this.currentServiceChain.children[0].children[0].tenant.wan_container_ip;
      this.logicTopologyData.children[0].subscriberIP = ip;
    };

    this.selectSubscriber = (subscriber) => {

      // append the device with to config settings
      serviceTopologyConfig.elWidths.push(160);

      this.addSubscriber(angular.copy(subscriber));

      //clean selected instances
      this.highlightInstances([]);

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
              // console.log(d3instance, instance);
              d3instance.selected = true;
              d3instance.stats = instance.stats; //add stats to d3 node
              d3instance.container = instance.container; // container info to d3 node
            }
            return d3instance;
          });
        });
      });

    }

    this.getInstanceStatus = (service) => {
      const deferred = $q.defer();

      let p;

      // subscriber specific
      if(this.currentSubscriber){

        let attr;
        try {
          attr = JSON.parse(service.tenant.service_specific_attribute);
        }
        catch(e){
          attr = null;
        }
        
        // if no instances are associated to the subscriber
        if(!attr || !attr.instance_id){
          let d = $q.defer();
          d.resolve([]);
          p = d.promise;
        }
        // if ther is an instance
        else{
          let instance = {};
          p = Instances.get({id: attr.instance_id}).$promise
          .then(function(_instance){
            instance = _instance;
            return Ceilometer.getInstanceStats(instance.instance_uuid);
          })
          .then((stats) => {
            instance.stats = stats;
            const containerName = `vcpe-${this.currentSubscriber.tags.sTag}-${this.currentSubscriber.tags.cTag}`;
            // append containers
            instance.container = {
              name: containerName
            };

            // TODO fetch container stats
            return Ceilometer.getContainerStats(containerName);
          })
          .then((containerStats) => {
            instance.container.stats = containerStats.stats;
            instance.container.port = containerStats.port;
            return [instance];
          });
        }
      }
      // global scope
      else {
        const param = {
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
