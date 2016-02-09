(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .directive('serviceTopology', function(){
    return {
      restrict: 'E',
      scope: {
        serviceChain: '='
      },
      bindToController: true,
      controllerAs: 'vm',
      template: '',
      controller: function($element, $window, $scope, d3, serviceTopologyConfig, ServiceRelation, Slice, Instances, Subscribers, TreeLayout){

        const el = $element[0];

        this.instances = [];
        this.slices = [];

        const width = el.clientWidth - (serviceTopologyConfig.widthMargin * 2);
        const height = el.clientHeight - (serviceTopologyConfig.heightMargin * 2);

        const treeLayout = d3.layout.tree()
          .size([height, width]);

        const svg = d3.select($element[0])
          .append('svg')
          .style('width', `${el.clientWidth}px`)
          .style('height', `${el.clientHeight}px`)

        const treeContainer = svg.append('g')
          .attr('transform', `translate(${serviceTopologyConfig.widthMargin * 4},${serviceTopologyConfig.heightMargin})`);

        var root;

        const draw = (tree) => {
          root = tree;
          root.x0 = height / 2;
          root.y0 = width / 2;

          TreeLayout.updateTree(treeContainer, treeLayout, root);
        };

        TreeLayout.drawLegend(svg);

        this.getInstances = (slice) => {
          Instances.query({slice: slice.id}).$promise
          .then((instances) => {
            this.selectedSlice = slice;
            this.instances = instances;
          })
        };
        
        $scope.$watch(() => this.serviceChain, (chain) => {
          if(chain){
            draw(chain);
          }
        });
      }
    }
  });

}());