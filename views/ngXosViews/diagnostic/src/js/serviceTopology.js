(function () {
  'use strict';

  angular.module('xos.diagnostic')
  .directive('serviceTopology', function(){
    return {
      restrict: 'E',
      scope: {
        serviceChain: '='
      },
      bindToController: true,
      controllerAs: 'vm',
      template: '',
      controller: function($element, $window, $scope, d3, serviceTopologyConfig, ServiceRelation, Slice, Instances, Subscribers, ServiceTopologyHelper){

        const el = $element[0];

        d3.select(window)
        .on('resize.service', () => {
          draw(this.serviceChain);
        });

        var root, svg;

        const draw = (tree) => {

          if(!tree){
            console.error('Tree is missing');
            return;
          }

          // TODO update instead clear and redraw

          // clean
          d3.select($element[0]).select('svg').remove();


          const width = el.clientWidth - (serviceTopologyConfig.widthMargin * 2);
          const height = el.clientHeight - (serviceTopologyConfig.heightMargin * 2);

          const treeLayout = d3.layout.tree()
            .size([height, width]);

          svg = d3.select($element[0])
            .append('svg')
            .style('width', `${el.clientWidth}px`)
            .style('height', `${el.clientHeight}px`)

          const treeContainer = svg.append('g')
            .attr('transform', `translate(${serviceTopologyConfig.widthMargin * 2},${serviceTopologyConfig.heightMargin})`);

          root = tree;
          root.x0 = height / 2;
          root.y0 = width / 2;

          // ServiceTopologyHelper.drawLegend(svg);
          ServiceTopologyHelper.updateTree(treeContainer, treeLayout, root, el);
        };
        
        $scope.$watch(() => this.serviceChain, (chain) => {
          if(angular.isDefined(chain)){
            draw(chain);
          }
        });
      }
    }
  });

}());