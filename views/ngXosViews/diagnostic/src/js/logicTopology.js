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
        var _this = this;

        const handleSvg = (el) => {

          d3.select($element[0]).select('svg').remove();

          svg = d3.select(el)
          .append('svg')
          .style('width', `${el.clientWidth}px`)
          .style('height', `${el.clientHeight}px`);
        }

        const loadGlobalScope = () => {
          ChartData.getLogicTree()
          .then((tree) => {
            LogicTopologyHelper.updateTree(svg);
          });
        }
        loadGlobalScope();

        $scope.$watch(() => this.selected, (selected) => {
          if(selected){
            ChartData.selectSubscriber(selected);
            LogicTopologyHelper.updateTree(svg);
          }
          else{
            ChartData.removeSubscriber();
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
          .catch(e => {
            _this.error = 'Service statistics are not available at this time. Please try again later.'
            $timeout(() => {
              _this.error = null;
            }, 2000);
          })
        });

        d3.select(window)
        .on('resize.logic', () => {
          handleSvg($element[0]);
          LogicTopologyHelper.setupTree(svg);
          LogicTopologyHelper.updateTree(svg);
        });

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
