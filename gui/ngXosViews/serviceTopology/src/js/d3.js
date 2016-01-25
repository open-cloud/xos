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
        d.y = d.depth * (($window.innerWidth - (serviceTopologyConfig.widthMargin * 2)) / maxDepth);
        console.log(d.id);
        if(d.type == 'slice'){
          console.info('slice found!', d);
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
        .attr('class', 'link')
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

      // empty panel
      //_this.slices = [];
      //_this.instances = [];

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

      //_this.selectedService = {
      //  id: d.id,
      //  name: d.name
      //};

      ServiceRelation.getServiceInterfaces(d.service.id)
        .then(interfaceTree => {

          const isDetailed = lodash.find(d.children, {type: 'slice'});
          if(isDetailed){
            d.selected = false;
            lodash.remove(d.children, {type: 'slice'});
          }
          else {
            d.selected = true;

            d.children = d.children.concat(interfaceTree);
          }

          updateTree(_svg, _layout, _source);
            // draw a rect with slice names
            //const parentNode = d3.select(this.parentNode);
            //parentNode
            //  .append('rect')
            //  .style('opacity', 0)
            //  .attr({
            //    width: 150,
            //    height: 50,
            //    y: 35,
            //    x: -75,
            //    class: 'slice-detail'
            //  })
            //  .transition()
            //  .duration(serviceTopologyConfig.duration)
            //  .style('opacity', 1);
            // TODO attach a click listener to draw instances and networks

            //parentNode
            //  .append('text')
            //  .style('opacity', 0)
            //  .attr({
            //    y: 65,
            //    x: -60,
            //    class: 'slice-name'
            //  })
            //  .text(() => {
            //    if(slices[0]){
            //      return slices[0].humanReadableName;
            //    }
            //
            //    return '';
            //  })
            //  .transition()
            //  .duration(serviceTopologyConfig.duration)
            //  .style('opacity', 1);
        });
    };

    this.updateTree = updateTree;
  });

}());