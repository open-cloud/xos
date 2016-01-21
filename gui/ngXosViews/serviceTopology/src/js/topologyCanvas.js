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
      controller: function($element, $window, d3, serviceTopologyConfig, ServiceRelation){

        // count the mas depth of an object
        const depthOf = (obj) => {
          var depth = 0;
          if (obj.children) {
            obj.children.forEach(function (d) {
              var tmpDepth = depthOf(d);
              if (tmpDepth > depth) {
                depth = tmpDepth
              }
            })
          }
          return 1 + depth
        };

        ServiceRelation.get()
          .then(res => {
            //console.log(res);
          });

        const treeData = [
          {
            'name': 'Top Level',
            'parent': 'null',
            'children': [
              {
                'name': 'Level 2: A',
                'parent': 'Top Level',
                'children': [
                  {
                    'name': 'Son of A',
                    'parent': 'Level 2: A'
                  },
                  {
                    'name': 'Daughter of A',
                    'parent': 'Level 2: A'
                  }
                ]
              },
              {
                'name': 'Level 2: B',
                'parent': 'Top Level'
              }
            ]
          }
        ];

        const width = $window.innerWidth - serviceTopologyConfig.widthMargin;
        const height = $window.innerHeight - serviceTopologyConfig.heightMargin;

        const tree = d3.layout.tree()
          .size([height, width]);

        const diagonal = d3.svg.diagonal()
          .projection(d => [d.y, d.x]);

        const svg = d3.select($element[0])
          .append('svg')
          .style('width', `${$window.innerWidth}px`)
          .style('height', `${$window.innerHeight}px`)
          .append('g')
          .attr("transform", "translate(" + serviceTopologyConfig.widthMargin+ "," + serviceTopologyConfig.heightMargin + ")");;

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
        var i = 0;
        var duration = 750;

        const draw = (tree) => {
          root = tree;
          root.x0 = $window.innerHeight / 2;
          root.y0 = 0;

          update(root);
        };

        function update(source) {

          const maxDepth = depthOf(source);

          // Compute the new tree layout.
          var nodes = tree.nodes(root).reverse(),
            links = tree.links(nodes);

          // Normalize for fixed-depth.
          nodes.forEach(function(d) {
            console.log(d);
            // 180 should be based on window.width and max node depth

            d.y = d.depth * (($window.innerWidth - (serviceTopologyConfig.widthMargin * 2)) / maxDepth);
            console.log(d.x);
          });

          // Update the nodes…
          var node = svg.selectAll('g.node')
            .data(nodes, function(d) { return d.id || (d.id = ++i); });

          // Enter any new nodes at the parent's previous position.
          var nodeEnter = node.enter().append('g')
            .attr('class', 'node')
            .attr('transform', function(d) {
              // this is the starting position
              return 'translate(' + source.y0 + ',' + source.x0 + ')';
            });
            //.on('click', click);

          nodeEnter.append('circle')
            .attr('r', 1e-6)
            .style('fill', function(d) { return d._children ? 'lightsteelblue' : '#fff'; });

          nodeEnter.append('text')
            .attr('x', function(d) { return d.children || d._children ? -13 : 13; })
            .attr('dy', '.35em')
            .attr('text-anchor', function(d) { return d.children || d._children ? 'end' : 'start'; })
            .text(function(d) { return d.name; })
            .style('fill-opacity', 1e-6);

          // Transition nodes to their new position.
          var nodeUpdate = node.transition()
            .duration(duration)
            .attr('transform', function(d) {
              return 'translate(' + d.y + ',' + d.x + ')';
            });

          nodeUpdate.select('circle')
            .attr('r', 10)
            .style('fill', function(d) { return d._children ? 'lightsteelblue' : '#fff'; });

          nodeUpdate.select('text')
            .style('fill-opacity', 1);

          // Transition exiting nodes to the parent's new position.
          var nodeExit = node.exit().transition()
            .duration(duration)
            .attr('transform', function(d) { return 'translate(' + source.y + ',' + source.x + ')'; })
            .remove();

          nodeExit.select('circle')
            .attr('r', 1e-6);

          nodeExit.select('text')
            .style('fill-opacity', 1e-6);

          // Update the links…
          var link = svg.selectAll('path.link')
            .data(links, function(d) { return d.target.id; });

          // Enter any new links at the parent's previous position.
          link.enter().insert('path', 'g')
            .attr('class', 'link')
            .attr('d', function(d) {
              var o = {x: source.x0, y: source.y0};
              return diagonal({source: o, target: o});
            });

          // Transition links to their new position.
          link.transition()
            .duration(duration)
            .attr('d', diagonal);

          // Transition exiting nodes to the parent's new position.
          link.exit().transition()
            .duration(duration)
            .attr('d', function(d) {
              var o = {x: source.x, y: source.y};
              return diagonal({source: o, target: o});
            })
            .remove();

          // Stash the old positions for transition.
          nodes.forEach(function(d) {
            d.x0 = d.x;
            d.y0 = d.y;
          });
        }

        ServiceRelation.get()
        .then((tree) => {
          console.log(tree);
          draw(tree);
        });
        //draw(treeData[0]);
      }
    }
  });

}());