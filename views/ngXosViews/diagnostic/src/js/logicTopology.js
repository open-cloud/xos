(function () {
  'use strict';
  angular.module('xos.diagnostic')
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
            LogicTopologyHelper.updateTree(svg);
          })
        })

        handleSvg($element[0]);
        LogicTopologyHelper.setupTree(svg);

        this.selectSubscriberModal = () => {
          this.openSelectSubscriberModal = true;
          $scope.$apply();
        };

        this.subscriberStatusModal = () => {
          this.openSubscriberStatusModal = true;
          $scope.$apply();
        };

        // listen for subscriber modal event
        $rootScope.$on('subscriber.modal.open', () => {

          if(ChartData.currentSubscriber){
            this.subscriberStatusModal();
          }
          else{
            this.selectSubscriberModal();
          }
        });

        // listen for subscriber modal event
        $rootScope.$on('subscriber.modal.open', () => {

          if(ChartData.currentSubscriber){
            this.currentSubscriber = ChartData.currentSubscriber;
            this.subscriberStatusModal();
          }
          else{
            this.selectSubscriberModal();
          }
        });

      }
    };
  });
})();
