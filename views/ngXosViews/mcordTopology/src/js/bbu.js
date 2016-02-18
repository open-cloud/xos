'use strict';

angular.module('xos.mcordTopology')
.service('NodeDrawer', function(){
  this.drawBbus = (nodes) => {
    nodes.append('circle')
      .attr({
        class: d => d.type,
        r: 15
      });

    nodes.append('text')
    .attr({
      'text-anchor': 'middle',
      y: 4
    })
    .text('BBU')
  };

  this.drawRrus = (nodes) => {

    nodes.append('circle')
      .attr({
        class: d => `${d.type}-shadow`,
        r: 30
      });
    
    nodes.append('circle')
      .attr({
        class: d => d.type,
        r: 10
      });
  };

  this.drawFabric = (nodes) => {
    nodes.append('rect')
      .attr({
        class: d => d.type,
        width: 20,
        height: 20,
        x: -10,
        y: -10
      });
  };

  this.drawOthers = (nodes) => {
    nodes.append('circle')
      .attr({
        class: d => d.type,
        r: 15
      });

    nodes.append('text')
    .attr({
      'text-anchor': 'middle',
      y: 4
    })
    .text(d => d.type)
  };
});