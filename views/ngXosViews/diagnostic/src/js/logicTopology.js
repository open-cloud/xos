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
      template: '',
      controller: function($element, $log, $scope, $rootScope, d3, LogicTopologyHelper, Node, Tenant, Ceilometer){
        $log.info('Logic Plane');

        var svg;


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

        $rootScope.$on('instance.detail', (evt, service) => {

          $log.info(`Highlight instance`, service)

          let param = {
            'service_vsg': {kind: 'vCPE'},
            'service_vbng': {kind: 'vBNG'},
            'service_volt': {kind: 'vOLT'}
          };

          Tenant.queryVsgInstances(param[service.name]).$promise
          .then((instances) => {
            console.log(instances);
            LogicTopologyHelper.getInstanceStatus(instances);
            LogicTopologyHelper.updateTree(svg);

            return Ceilometer.getInstancesStats(instances);
          })
          .then((stats) => {
            console.log('stats', stats);
          })
          .catch((e) => {
            throw new Error(e);
          });
        })

        handleSvg($element[0]);
        LogicTopologyHelper.setupTree(svg);

      }
    };
  });
})();
