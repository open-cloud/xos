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
      controller: function($element, $log, $scope, $rootScope, $timeout, d3, LogicTopologyHelper, Node, Tenant, Ceilometer, serviceTopologyConfig, ChartData){
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

        ChartData.getLogicTree()
        .then((tree) => {
          LogicTopologyHelper.updateTree(svg);
        });

        $scope.$watch(() => this.selected, (selected) => {
          if(selected){
            ChartData.selectSubscriber(selected);
            LogicTopologyHelper.updateTree(svg);
          }
        });

        $rootScope.$on('instance.detail.hide', () => {
          this.hideInstanceStats = true;
          $timeout(() => {
            this.selectedInstances = [];
            ChartData.highlightInstances([]);
            LogicTopologyHelper.updateTree(svg);
          }, 500);
        });

        $rootScope.$on('instance.detail', (evt, service) => {
          ChartData.getInstanceStatus(service)
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
            LogicTopologyHelper.updateTree(svg);
          })
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
