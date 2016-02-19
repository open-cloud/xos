'use strict';

angular.module('xos.mcordTopology')
.service('NodeDrawer', function(){

  const duration = 500;

  this.drawFabricBox = (svg, hStep, vStep) => {
    let fabric = svg.append('g')
    .attr({
      transform: `translate(${hStep - 25}, ${vStep - 25})`
    });

    fabric.append('rect')
      .attr({
        width: hStep + 50,
        height: vStep + 50,
        class: 'fabric-container'
      });

    fabric.append('text')
    .text('Fabric')
    .attr({
      'text-anchor': 'middle',
      x: ((hStep + 50) / 2),
      y: -10
    });
  };

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
      'text-anchor': 'start',
      y: 17,
      x: 17,
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
        x: -15,
        y: -15,
        opacity: 0
      })
      .transition()
      .duration(duration)
      // .delay((d, i) => i * (duration / 2))
      .attr({
        width: 30,
        height: 30,
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
      'text-anchor': 'start',
      y: 17,
      x: 17,
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