'use strict';

angular.module('xos.mcordTopology')
.service('NodeDrawer', function(){

  const duration = 500;

  this.drawBbus = (nodes) => {

    nodes.append('circle')
      .attr({
        class: d => d.type,
        r: 0,
        opacity: 0
      })
      .transition()
      .duration(duration)
      // .delay((d, i) => i * (duration / 2))
      .attr({
        r: 15,
        opacity: 1
      });

    nodes.append('text')
    .attr({
      'text-anchor': 'middle',
      y: 4,
      opacity: 0
    })
    .text(d => `BBU ${d.name.substr(d.name.length - 1, 1)}`)
    .transition()
    .duration(duration * 2)
    .attr({
      opacity: 1
    });
  };

  this.drawRrus = (nodes) => {

    nodes.append('circle')
      .attr({
        class: d => `${d.type}-shadow`,
        r: 0,
        opacity: 0
      })
      .transition()
      .duration(duration * 2)
      // .delay((d, i) => i * (duration / 2))
      .attr({
        r: 30,
        opacity: 1
      });
  
    nodes.append('circle')
      .attr({
        class: d => d.type,
        r: 0,
        opacity: 0
      })
      .transition()
      .duration(duration)
      // .delay((d, i) => i * (duration / 2))
      .attr({
        r: 10,
        opacity: 1
      });
  };

  this.drawFabric = (nodes) => {
    nodes.append('rect')
      .attr({
        class: d => d.type,
        width: 0,
        height: 0,
        x: -10,
        y: -10,
        opacity: 0
      })
      .transition()
      .duration(duration)
      // .delay((d, i) => i * (duration / 2))
      .attr({
        width: 20,
        height: 20,
        opacity: 1
      });
  };

  this.drawOthers = (nodes) => {
    nodes.append('circle')
      .attr({
        class: d => d.type,
        r: 0,
        opacity: 0
      })
      .transition()
      .duration(duration)
      // .delay((d, i) => i * (duration / 2))
      .attr({
        r: 15,
        opacity: 1
      });

    nodes.append('text')
    .attr({
      'text-anchor': 'middle',
      y: 4,
      opacity: 0
    })
    .text(d => d.type)
    .transition()
    .duration(duration * 2)
    .attr({
      opacity: 1
    });

  };
  
  this.removeElements = (nodes) => {
    nodes
    .transition()
    .duration(duration)
    .attr({
      opacity: 0
    })
    .remove();
  };
});