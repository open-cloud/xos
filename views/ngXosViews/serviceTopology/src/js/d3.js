(function () {
  'use strict';

  angular.module('xos.serviceTopology')
    .factory('d3', function($window){
      return $window.d3;
    })
  .service('TreeLayout', function($window, lodash, ServiceRelation, serviceTopologyConfig, Slice, Instances){

    const drawLegend = (svg) => {
      const legendContainer = svg.append('g')
        .attr({
          class: 'legend'
        });

      legendContainer.append('rect')
      .attr({
        transform: d => `translate(10, 80)`,
        width: 100,
        height: 100
      });

      // service
      const service = legendContainer.append('g')
      .attr({
        class: 'node service'
      });

      service.append('circle')
      .attr({
        r: serviceTopologyConfig.circle.radius,
        transform: d => `translate(30, 100)`
      });

      service.append('text')
      .attr({
        transform: d => `translate(45, 100)`,
        dy: '.35em'
      })
      .text('Service')
        .style('fill-opacity', 1);

      // slice
      const slice = legendContainer.append('g')
        .attr({
          class: 'node slice'
        });

      slice.append('rect')
        .attr({
          width: 20,
          height: 20,
          x: -10,
          y: -10,
          transform: d => `translate(30, 130)`
        });

      slice.append('text')
        .attr({
          transform: d => `translate(45, 130)`,
          dy: '.35em'
        })
        .text('Slices')
        .style('fill-opacity', 1);

      // instance
      const instance = legendContainer.append('g')
        .attr({
          class: 'node instance'
        });

      instance.append('rect')
        .attr({
          width: 20,
          height: 20,
          x: -10,
          y: -10,
          transform: d => `translate(30, 160)`
        });

      instance.append('text')
        .attr({
          transform: d => `translate(45, 160)`,
          dy: '.35em'
        })
        .text('Instances')
        .style('fill-opacity', 1);
    };

    var _svg, _layout, _source;

    var i = 0;

    const getInitialNodePosition = (node, source, direction = 'enter') => {
      // this is the starting position
      // TODO if enter use y0 and x0 else x and y
      // TODO start from the node that has been clicked
      if(node.parent){
        if(direction === 'enter' && node.parent.y0 && node.parent.x0){
          return `translate(${node.parent.y0},${node.parent.x0})`;
        }
        return `translate(${node.parent.y},${node.parent.x})`;
      }
      return `translate(${source.y0},${source.x0})`;
    };

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
        }
      });

      // Update the nodes…
      var node = svg.selectAll('g.node')
        .data(nodes, function(d) { return d.id || (d.id = ++i); });

      // Enter any new nodes at the parent's previous position.
      var nodeEnter = node.enter().append('g')
        .attr({
          class: d => `node ${d.type}`,
          transform: d => getInitialNodePosition(d, source)
        });

      const subscriberNodes = nodeEnter.filter('.subscriber');
      const internetNodes = nodeEnter.filter('.internet');
      const serviceNodes = nodeEnter.filter('.service');
      const instanceNodes = nodeEnter.filter('.instance');
      const sliceNodes = nodeEnter.filter('.slice');

      subscriberNodes.append('path')
        .attr({
          d: 'M20.771,12.364c0,0,0.849-3.51,0-4.699c-0.85-1.189-1.189-1.981-3.058-2.548s-1.188-0.454-2.547-0.396c-1.359,0.057-2.492,0.792-2.492,1.188c0,0-0.849,0.057-1.188,0.397c-0.34,0.34-0.906,1.924-0.906,2.321s0.283,3.058,0.566,3.624l-0.337,0.113c-0.283,3.283,1.132,3.68,1.132,3.68c0.509,3.058,1.019,1.756,1.019,2.548s-0.51,0.51-0.51,0.51s-0.452,1.245-1.584,1.698c-1.132,0.452-7.416,2.886-7.927,3.396c-0.511,0.511-0.453,2.888-0.453,2.888h26.947c0,0,0.059-2.377-0.452-2.888c-0.512-0.511-6.796-2.944-7.928-3.396c-1.132-0.453-1.584-1.698-1.584-1.698s-0.51,0.282-0.51-0.51s0.51,0.51,1.02-2.548c0,0,1.414-0.397,1.132-3.68H20.771z',
          transform: 'translate(-20, -20)'
        });

      internetNodes.append('path')
        .attr({
          d: 'M209,15a195,195 0 1,0 2,0zm1,0v390m195-195H15M59,90a260,260 0 0,0 302,0 m0,240 a260,260 0 0,0-302,0M195,20a250,250 0 0,0 0,382 m30,0 a250,250 0 0,0 0-382',
          stroke: '#000',
          'stroke-width': '20px',
          fill: 'none',
          transform: 'translate(-10, -10), scale(0.05)'
        });

      serviceNodes.append('circle')
        .attr('r', 1e-6)
        .style('fill', d => d._children ? 'lightsteelblue' : '#fff')
        .on('click', serviceClick);

      sliceNodes.append('rect')
        .attr({
          width: 20,
          height: 20,
          x: -10,
          y: -10
        });

      instanceNodes.append('rect')
        .attr({
          width: 20,
          height: 20,
          x: -10,
          y: -10,
          class: d => d.active ?'' : 'active'
        });

      nodeEnter.append('text')
        .attr({
          x: d => d.children ? -serviceTopologyConfig.circle.selectedRadius -3 : serviceTopologyConfig.circle.selectedRadius + 3,
          dy: '.35em',
          transform: d => {
            if (d.children && d.parent){
              if(d.parent.x < d.x){
                return 'rotate(-30)';
              }
              return 'rotate(30)';
            }
          },
          'text-anchor': d => d.children ? 'end' : 'start'
        })
        .text(d => d.name)
        .style('fill-opacity', 1e-6);

      // Transition nodes to their new position.
      var nodeUpdate = node.transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          'transform': d => `translate(${d.y},${d.x})`
        });

      nodeUpdate.select('circle')
        .attr('r', d => d.selected ? serviceTopologyConfig.circle.selectedRadius : serviceTopologyConfig.circle.radius)
        .style('fill', d => d.selected ? 'lightsteelblue' : '#fff');

      nodeUpdate.select('text')
        .style('fill-opacity', 1);

      // Transition exiting nodes to the parent's new position.
      var nodeExit = node.exit().transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          'transform': d => getInitialNodePosition(d, source, 'exit')
        })
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
        .attr('class', d => `link ${d.target.type} ${d.target.active ? '' : 'active'}`)
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

      if(!d.service){
        return;
      }

      // toggling selected status
      d.selected = !d.selected;

      var selectedNode = d3.select(this);

      selectedNode
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr('r', serviceTopologyConfig.circle.selectedRadius);

      ServiceRelation.getServiceInterfaces(d.service)
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
    this.drawLegend = drawLegend;
  });

}());