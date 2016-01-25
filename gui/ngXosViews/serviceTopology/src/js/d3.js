(function () {
  'use strict';

  angular.module('xos.serviceTopology')
    .factory('d3', function($window){
      return $window.d3;
    })
  .service('TreeLayout', function($window, lodash, ServiceRelation, serviceTopologyConfig, Slice, Instances){

    var _svg, _layout, _source;

    var i = 0;

    // given a canvas, a layout and a data source, draw a tree layout
    const updateTree = (svg, layout, source) => {

      //cache data
      _svg = svg;
      _layout = layout;
      _source = source;

      const maxDepth = ServiceRelation.depthOf(source);

      const diagonal = d3.svg.diagonal()
        .projection(d => [d.y, d.x]);

      // Compute the new tree layout.
      var nodes = layout.nodes(source).reverse(),
        links = layout.links(nodes);

      // Normalize for fixed-depth.
      nodes.forEach(function(d) {
        // position the child node horizontally
        const step = (($window.innerWidth - (serviceTopologyConfig.widthMargin * 2)) / maxDepth);
        d.y = d.depth * step;
        if(d.type === 'slice' || d.type === 'instance'){
          d.y = d.depth * step - (step / 2);
          //d.x = d.parent.x + (step / 2);
          //console.log(d.parent);
        }
      });

      // Update the nodes…
      var node = svg.selectAll('g.node')
        .data(nodes, function(d) { return d.id || (d.id = ++i); });

      // Enter any new nodes at the parent's previous position.
      var nodeEnter = node.enter().append('g')
        .attr({
          class: d => `node ${d.type}`,
          transform: d => `translate(${source.y0},${source.x0})` // this is the starting position
        });

      // TODO append different shapes base on type
      nodeEnter.append('circle')
        .attr('r', 1e-6)
        .style('fill', d => d._children ? 'lightsteelblue' : '#fff')
        .on('click', serviceClick);

      nodeEnter.append('text')
        .attr('x', function(d) { return d.children || d._children ? -13 : 13; })
        .attr('transform', function(d) {
          if((d.children || d._children) && d.parent || d._parent){
            return 'rotate(30)';
          }
        })
        .attr('dy', '.35em')
        .attr('text-anchor', function(d) { return d.children || d._children ? 'end' : 'start'; })
        .text(function(d) { return d.name; })
        .style('fill-opacity', 1e-6);

      // Transition nodes to their new position.
      var nodeUpdate = node.transition()
        .duration(serviceTopologyConfig.duration)
        .attr('transform', function(d) {
          return 'translate(' + d.y + ',' + d.x + ')';
        });

      nodeUpdate.select('circle')
        .attr('r', d => d.selected ? 15 : 10)
        .style('fill', function(d) { return d._children ? 'lightsteelblue' : '#fff'; });

      nodeUpdate.select('text')
        .style('fill-opacity', 1);

      // Transition exiting nodes to the parent's new position.
      var nodeExit = node.exit().transition()
        .duration(serviceTopologyConfig.duration)
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
        .attr('class', d => `link ${d.target.type}`)
        .attr('d', function(d) {
          var o = {x: source.x0, y: source.y0};
          return diagonal({source: o, target: o});
        });

      // Transition links to their new position.
      link.transition()
        .duration(serviceTopologyConfig.duration)
        .attr('d', diagonal);

      // Transition exiting nodes to the parent's new position.
      link.exit().transition()
        .duration(serviceTopologyConfig.duration)
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
    };

    const serviceClick = function(d) {

      // toggling selected status
      d.selected = !d.selected;

      // reset all the nodes to default radius
      var nodes = d3.selectAll('circle')
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr('r', 10);

      // remove slices details
      d3.selectAll('rect.slice-detail')
        .remove();
      d3.selectAll('text.slice-name')
        .remove();

      var selectedNode = d3.select(this);

      selectedNode
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr('r', 15);

      if(!d.service){
        return;
      }

      ServiceRelation.getServiceInterfaces(d.service.id)
        .then(interfaceTree => {

          const isDetailed = lodash.find(d.children, {type: 'slice'});
          if(isDetailed){
            lodash.remove(d.children, {type: 'slice'});
          }
          else {
            d.children = d.children.concat(interfaceTree);
          }

          updateTree(_svg, _layout, _source);
        });
    };

    this.updateTree = updateTree;
  });

}());