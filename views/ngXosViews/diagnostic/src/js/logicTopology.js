(function () {
  'use strict';
  angular.module('xos.serviceTopology')
  .directive('logicTopology', function(){
    return {
      restrict: 'E',
      scope: {
        subscribers: '=',
        selected: '='
      },
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/logicTopology.tpl.html',
      controller: function($element, $log, $scope, $rootScope, $timeout, d3, LogicTopologyHelper, Node, Tenant, Ceilometer){
        $log.info('Logic Plane');

        var svg;
        this.selectedInstances = [];
        this.hideInstanceStats = true;

        const handleSvg = (el) => {

          svg = d3.select(el)
          .append('svg')
          .style('width', `${el.clientWidth}px`)
          .style('height', `${el.clientHeight}px`);
        }

        $scope.$watch(() => this.subscribers, (subscribers) => {
          if(subscribers){

            // LogicTopologyHelper.addSubscribers(angular.copy(subscribers));

            Node.queryWithInstances().$promise
            .then((computeNodes) => {
              LogicTopologyHelper.addComputeNodes(computeNodes);
              LogicTopologyHelper.updateTree(svg);
            });
            
          }
        });

        $scope.$watch(() => this.selected, (selected) => {
          if(selected){
            $log.info(`Update logic layer for subscriber ${selected.humanReadableName}`);
          }
        });

        $rootScope.$on('instance.detail.hide', () => {
          this.hideInstanceStats = true;
          $timeout(() => {
            this.selectedInstances = [];
            LogicTopologyHelper.getInstanceStatus([]);
            LogicTopologyHelper.updateTree(svg);
          }, 500);
        });

        $rootScope.$on('instance.detail', (evt, service) => {

          let param = {
            'service_vsg': {kind: 'vCPE'},
            'service_vbng': {kind: 'vBNG'},
            'service_volt': {kind: 'vOLT'}
          };

          Tenant.queryVsgInstances(param[service.name]).$promise
          .then((instances) => {

            return Ceilometer.getInstancesStats(instances);
          })
          .then((instances) => {
            this.hideInstanceStats = false;
            // HACK if array is empty wait for animation
            if(instances.length === 0){
              this.hideInstanceStats = true;
              $timeout(() => {
                this.selectedInstances = instances;
              }, 500);
            }
            else{
              this.selectedInstances = instances;
            }
            
            LogicTopologyHelper.getInstanceStatus(instances);
            LogicTopologyHelper.updateTree(svg);
          })
          .catch((e) => {
            throw new Error(e);
          });
        })

        handleSvg($element[0]);
        LogicTopologyHelper.setupTree(svg);

        this.openSubscriberModal = () => {
          this.subscriberModal = true;
          $scope.$apply();
        };


        // listen for subscriber modal event
        $rootScope.$on('subscriber.modal.open', () => {
          this.openSubscriberModal();
        });

      }
    };
  });
})();
