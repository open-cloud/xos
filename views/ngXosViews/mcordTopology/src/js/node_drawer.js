
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


'use strict';

angular.module('xos.mcordTopology')
.service('NodeDrawer', function(TopologyElements){

  const duration = 500;

  let isFabricDrawed = false;

  this.drawFabricBox = (svg, hStep, vStep) => {

    if(isFabricDrawed){
      return;
    }

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

    // fabric.append('text')
    // .text('Fabric')
    // .attr({
    //   'text-anchor': 'middle',
    //   x: ((hStep + 50) / 2),
    //   y: -10
    // });

    isFabricDrawed = true;
  };

  this.drawBbus = (nodes) => {

    nodes.append('rect')
      .attr({
        class: d => d.type,
        width: 30,
        height: 30,
        x: -15,
        y: -15,
        opacity: 0
      })
      .transition()
      .duration(duration)
      .attr({
        r: 15,
        opacity: 1
      });

    nodes
      .append('path')
      .attr({
        class: d => `${d.type} antenna`,
        opacity: 0,
        d: () => TopologyElements.icons.bbu,
        transform: `translate(-18, -18)`
      })
      .transition()
      .duration(duration)
      .attr({
        opacity: 1
      });

    nodes.append('text')
    .attr({
      'text-anchor': 'start',
      y: 25,
      x: 5,
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
        r: 40,
        opacity: 1
      });

    nodes
      .append('path')
      .attr({
        class: d => `${d.type} antenna`,
        opacity: 0,
        d: () => TopologyElements.icons.rru,
        transform: `translate(-18, -18)`
      })
      .transition()
      .duration(duration)
      .attr({
        opacity: 1
      });
  
    // nodes.append('circle')
    //   .attr({
    //     class: d => d.type,
    //     r: 0,
    //     opacity: 0
    //   })
    //   .transition()
    //   .duration(duration)
    //   // .delay((d, i) => i * (duration / 2))
    //   .attr({
    //     r: 10,
    //     opacity: 1
    //   });
  };

  this.drawFabric = (nodes) => {
    nodes
      .append('rect')
      .attr({
        width: 30,
        height: 30,
        x: -15,
        y: -15
      });

    nodes
      .append('path')
      .attr({
        class: d => d.type,
        opacity: 0,
        d: () => TopologyElements.icons.switch,
        transform: `translate(-22, -22), scale(0.4)`
      })
      .transition()
      .duration(duration)
      // .delay((d, i) => i * (duration / 2))
      .attr({
        opacity: 1
      });
  };

  this.drawOthers = (nodes) => {
    nodes.append('rect')
      .attr({
        class: d => d.type,
        width: 30,
        height: 30,
        x: -15,
        y: -15,
        opacity: 0
      })
      .transition()
      .duration(duration)
      .attr({
        r: 15,
        opacity: 1
      });

    nodes
      .append('path')
      .attr({
        class: d => `${d.type} antenna`,
        opacity: 0,
        d: () => TopologyElements.icons.bbu,
        transform: `translate(-18, -18)`
      })
      .transition()
      .duration(duration)
      .attr({
        opacity: 1
      });

    nodes.append('text')
    .attr({
      'text-anchor': 'start',
      y: 25,
      x: -12,
      opacity: 0
    })
    .text(d => d.name.toUpperCase())
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