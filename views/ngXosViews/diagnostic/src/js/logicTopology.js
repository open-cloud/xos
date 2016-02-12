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
      controller: function($element, $log, $scope, d3, LogicTopologyHelper){
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

            // TODO
            // build here the full data structure

            LogicTopologyHelper.addSubscribers(svg, angular.copy(subscribers));
          }
        });

        $scope.$watch(() => this.selected, (selected) => {
          if(selected){
            $log.info(`Update logic layer for subscriber ${selected.humanReadableName}`);
          }
        });

        handleSvg($element[0]);
        LogicTopologyHelper.drawTree(svg);
      }
    };
  });
})();
