(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .directive('serviceCanvas', function(){
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/topology_canvas.tpl.html',
      controller: function($element, $window, d3, serviceTopologyConfig, ServiceRelation, Slice, Instances, Subscribers, TreeLayout){

        this.instances = [];
        this.slices = [];

        const width = $window.innerWidth - serviceTopologyConfig.widthMargin;
        const height = $window.innerHeight - serviceTopologyConfig.heightMargin;

        const treeLayout = d3.layout.tree()
          .size([height, width]);

        const svg = d3.select($element[0])
          .append('svg')
          .style('width', `${$window.innerWidth}px`)
          .style('height', `${$window.innerHeight}px`)
          .append('g')
          .attr('transform', 'translate(' + serviceTopologyConfig.widthMargin+ ',' + serviceTopologyConfig.heightMargin + ')');

        //const resizeCanvas = () => {
        //  var targetSize = svg.node().getBoundingClientRect();
        //
        //  d3.select(self.frameElement)
        //    .attr('width', `${targetSize.width}px`)
        //    .attr('height', `${targetSize.height}px`)
        //};
        //d3.select(window)
        //  .on('load', () => {
        //    resizeCanvas();
        //  });
        //d3.select(window)
        //  .on('resize', () => {
        //    resizeCanvas();
        //    update(root);
        //  });
        var root;

        const draw = (tree) => {
          root = tree;
          root.x0 = $window.innerHeight / 2;
          root.y0 = 0;

          TreeLayout.updateTree(svg, treeLayout, root);
        };

        var _this = this;

        Subscribers.query().$promise
        .then((subscribers) => {
          this.subscribers = subscribers;
          if(subscribers.length === 1){
            this.selectedSubscriber = subscribers[0];
            this.getServiceChain(this.selectedSubscriber);
          }
        });

        this.getInstances = (slice) => {
          Instances.query({slice: slice.id}).$promise
          .then((instances) => {
            this.selectedSlice = slice;
            this.instances = instances;
          })
        };

        // redraw when subrsbiber change
        this.getServiceChain = (subscriber) => {
          ServiceRelation.get(subscriber)
            .then((tree) => {
              draw(tree);
            });
        };
      }
    }
  });

}());