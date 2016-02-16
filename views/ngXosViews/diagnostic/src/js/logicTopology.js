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
      controller: function($element, $log, $scope, $rootScope, d3, LogicTopologyHelper, Node){
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

            LogicTopologyHelper.addSubscribers(angular.copy(subscribers));

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

        $rootScope.$on('instance.detail', (evt, instance) => {

          $log.info(`Highlight instance; ${instance.id}`)

          LogicTopologyHelper.getInstanceStatus(instance.id);
          LogicTopologyHelper.updateTree(svg);
        })

        handleSvg($element[0]);
        LogicTopologyHelper.setupTree(svg);
      }
    };
  });
})();
