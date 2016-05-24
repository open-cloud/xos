(function () {
  'use strict';

  const shapes = {
    cloud: ' M 79.72 49.60 C 86.00 37.29 98.57 29.01 111.96 26.42 C 124.27 24.11 137.53 26.15 148.18 32.90 C 158.08 38.78 165.39 48.87 167.65 60.20 C 176.20 57.90 185.14 56.01 194.00 57.73 C 206.08 59.59 217.92 66.01 224.37 76.66 C 227.51 81.54 228.85 87.33 229.23 93.06 C 237.59 93.33 246.22 95.10 253.04 100.19 C 256.69 103.13 259.87 107.67 258.91 112.59 C 257.95 118.43 252.78 122.38 247.78 124.82 C 235.27 130.43 220.23 130.09 207.98 123.93 C 199.33 127.88 189.76 129.43 180.30 128.57 C 173.70 139.92 161.70 147.65 148.86 149.93 C 133.10 153.26 116.06 148.15 104.42 137.08 C 92.98 143.04 78.96 143.87 66.97 139.04 C 57.75 135.41 49.70 128.00 46.60 118.43 C 43.87 109.95 45.81 100.29 51.30 93.32 C 57.38 85.18 67.10 80.44 76.99 78.89 C 74.38 69.20 74.87 58.52 79.72 49.60 Z'
  }

  var computeNodeId = 0;
  var instanceId = 0;

  angular.module('xos.diagnostic')
  .service('NodeDrawer', function(d3, serviceTopologyConfig, RackHelper, _){

    var _this = this;

    this.addNetworks = (nodes) => {

      // clean childs
      nodes.selectAll('*').remove();

      nodes.append('path')
      .attr({
        d: shapes.cloud,
        transform: 'translate(-100, -72), scale(0.7)',
        class: 'cloud'
      });

      nodes.append('text')
      .attr({
        'text-anchor': 'middle',
        y: -5,
        x: 5,
      })
      .text(d => d.name)

      nodes.append('text')
      .attr({
        'text-anchor': 'middle',
        y: 8,
        x: 5,
        class: 'small'
      })
      .text(d => d.subtitle)

      nodes.each(function(n){
        let currentNode = d3.select(this);
        // cicle trouch node to add Tags and Public IP
        if(n.name === 'LAN-Side' && angular.isDefined(n.subscriberTag)){
          currentNode.append('text')
          .attr({
            'text-anchor': 'middle',
            y: 50
          })
          .text(() => `C-Tag: ${n.subscriberTag.cTag}`);

          currentNode.append('text')
          .attr({
            'text-anchor': 'middle',
            y: 70
          })
          .text(() => `S-Tag: ${n.subscriberTag.sTag}`);
        }

        if(n.name === 'WAN-Side' && angular.isDefined(n.subscriberIP)){
          currentNode.append('text')
          .attr({
            'text-anchor': 'middle',
            y: 50
          })
          .text(() => `Public IP: ${n.subscriberIP}`);
        }
      });
    }

    this.addRack = (nodes) => {

      // loop because of D3
      // rack will be only one
      nodes.each(d => {
        let [w, h] = RackHelper.getRackSize(d.computeNodes);

        // TODO update instead of delete and redraw
        nodes.select('g').remove();

        let rack = nodes
        .append('g');

        rack
        .attr({
          transform: `translate(0,0)`
        })
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          transform: () => `translate(${- (w / 2)}, ${- (h / 2)})`
        });

        rack
        .append('rect')
        .attr({
          width: 0,
          height: 0
        })
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          width: w,
          height: h
        });

        rack.append('text')
        .attr({
          'text-anchor': 'middle',
          y: - 10,
          x: w / 2,
          opacity: 0
        })
        .text(d => d.name)
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          opacity: 1
        })

        this.drawComputeNodes(rack, d.computeNodes);

      });

    };

    this.drawComputeNodes = (container, nodes) => {
      
      let elements = container.selectAll('.compute-nodes')
      .data(nodes, d => {
        if(!angular.isString(d.d3Id)){
          d.d3Id = `compute-node-${++computeNodeId}`;
        }
        return d.d3Id;
      });

      let {width, height} = container.node().getBoundingClientRect();

      var nodeContainer = elements.enter().append('g');

      nodeContainer
      .attr({
        transform: `translate(${width / 2}, ${ height / 2})`,
        class: 'compute-node',
      })
      .transition()
      .duration(serviceTopologyConfig.duration)
      .attr({
        transform: (d) => `translate(${RackHelper.getComputeNodePosition(nodes, d.d3Id.replace('compute-node-', '') - 1)})`
      });

      nodeContainer.append('rect')
      .attr({
        width: 0,
        height: 0
      })
      .transition()
      .duration(serviceTopologyConfig.duration)
      .attr({
        width: d => RackHelper.getComputeNodeSize(d.instances)[0],
        height: d => RackHelper.getComputeNodeSize(d.instances)[1],
      });

      nodeContainer.append('text')
      .attr({
        'text-anchor': 'start',
        y: 17, //FIXME
        x: 10, //FIXME
        opacity: 0
      })
      .text(d => d.humanReadableName.split('.')[0])
      .transition()
      .duration(serviceTopologyConfig.duration)
      .attr({
        opacity: 1
      })

      // if there are Compute Nodes
      if(nodeContainer.length > 0){
        // draw instances for each compute node
        nodeContainer.each(function(a){
          _this.drawInstances(d3.select(this), a.instances);
        })
      }

    };

    // NOTE Stripping unuseful names to shorten labels.
    // This is not elegant
    const formatInstanceName = (name) => {
      return name
        .replace('app_', '')
        .replace('service_', '')
        // .replace('ovs_', '')
        .replace('mysite_', '')
        .replace('_instance', '');
    };

    const getInstanceStatusColor = (instance) => {
      function startWith(val, string){
        return string.substring(0, val.length) === val;
      }

      if(startWith('0 - ', instance.backend_status)){
        return 'provisioning';
      }
      if(startWith('1 - ', instance.backend_status)){
        return 'good';
      }
      if(startWith('2 - ', instance.backend_status)){
        return 'bad';
      }
      else {
        return '';
      }
    };

    const drawContainer = (container, docker) => {

      const containerBox = container.append('g')
        .attr({
          class: 'container',
          transform: `translate(${serviceTopologyConfig.instance.margin}, 115)`
        });

      containerBox.append('rect')
        .attr({
          width: 250 - (serviceTopologyConfig.container.margin * 2),
          height: serviceTopologyConfig.container.height,
        });

      containerBox.append('text')
        .attr({
          y: 20,
          x: serviceTopologyConfig.instance.margin,
          class: 'name'
        })
        .text(docker.name)

      // add stats
      const interestingMeters = ['memory', 'memory.usage', 'cpu_util'];

      interestingMeters.forEach((m, i) => {
        const meter = _.find(docker.stats, {meter: m});
        // if there is no meter stats skip rendering
        if(!angular.isDefined(meter)){
          return;
        }
        containerBox.append('text')
        .attr({
          y: 40 + (i * 15),
          x: serviceTopologyConfig.instance.margin,
          opacity: 0
        })
        .text(`${meter.description}: ${Math.round(meter.value)} ${meter.unit}`)
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          opacity: 1
        });
      });

      // add port stats
      const ports = ['eth0', 'eth1'];
      const interestingPortMeters = [
        {
          meter: 'network.incoming.bytes.rate',
          label: 'Incoming'
        },
        {
          meter: 'network.outgoing.bytes.rate',
          label: 'Outgoing'
        }
      ];
      
      ports.forEach((p, j) => {

        // if there are no port stats skip rendering
        if(docker.port[p].length === 0){
          return;
        }

        containerBox.append('text')
        .attr({
          y: 90,
          x: serviceTopologyConfig.instance.margin + (120 * j),
          class: 'name'
        })
        .text(`${docker.name}-${p}`)

        interestingPortMeters.forEach((m, i) => {

          const meter = _.find(docker.port[p], {meter: m.meter});
          // if there is no meter stats skip rendering
          if(!angular.isDefined(meter)){
            return;
          }
          containerBox.append('text')
          .attr({
            y: 105 + (i * 15),
            x: serviceTopologyConfig.instance.margin + (120 * j),
            opacity: 0
          })
          .text(`${m.label}: ${Math.round(meter.value)} ${meter.unit}`)
          .transition()
          .duration(serviceTopologyConfig.duration)
          .attr({
            opacity: 1
          });
        });
      });
    }

    const showInstanceStats = (container, instance) => {

      // NOTE this should be dinamically positioned
      // base on the number of element present

      // fake the position
      let translation = {
        'mysite_vsg-1': '200, -120',
        'mysite_vsg-2': '-300, 30',
        'mysite_vsg-3': '-300, -250',
      };

      const statsContainer = container.append('g')
        .attr({
          transform: `translate(${translation[instance.humanReadableName] || translation['mysite_vsg-1']})`,
          class: 'stats-container'
        })
        .on('click', function(d) {
          // toggling visisbility
          d.fade = !d.fade;
          let opacity;
          if(d.fade){
            opacity = 0.1;
          }
          else{
            opacity = 1;
          }

          d3.select(this)
          .transition()
          .duration(serviceTopologyConfig.duration)
          .attr({
            opacity: opacity
          })
        });

      let lines = {
        'mysite_vsg-1': {
          x1: -160,
          y1: 120,
          x2: 0,
          y2: 50,
        },
        'mysite_vsg-2': {
          x1: 250,
          y1: 50,
          x2: 300,
          y2: -10
        },
        'mysite_vsg-3': {
          x1: 250,
          y1: 50,
          x2: 300,
          y2: 270
        }
      }

      statsContainer.append('line')
        .attr({
          x1: d => lines[d.humanReadableName].x1 || lines['mysite_vsg-1'].x1,
          y1: d => lines[d.humanReadableName].y1 || lines['mysite_vsg-1'].y1,
          x2: d => lines[d.humanReadableName].x2 || lines['mysite_vsg-1'].x2,
          y2: d => lines[d.humanReadableName].y2 || lines['mysite_vsg-1'].y2,
          stroke: 'black',
          opacity: 0
        })
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          opacity: 1
        })

      // NOTE rect should be dinamically sized base on the presence of a container
      let statsHeight = 110;
      let statsWidth = 250;

      if (instance.container){
        statsHeight += serviceTopologyConfig.container.height + (serviceTopologyConfig.container.margin * 2)
      }

      const statsVignette = statsContainer.append('rect')
        .attr({
          width: statsWidth,
          height: statsHeight,
          opacity: 0
        })
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          opacity: 1
        });


      // add instance info
      statsContainer.append('text')
        .attr({
          y: 15,
          x: serviceTopologyConfig.instance.margin,
          class: 'name',
          opacity: 0
        })
        .text(instance.humanReadableName)
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          opacity: 1
        })

      statsContainer.append('text')
        .attr({
          y: 30,
          x: serviceTopologyConfig.instance.margin,
          class: 'ip',
          opacity: 0
        })
        .text(instance.ip)
        .transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          opacity: 1
        })

      // add stats
      const interestingMeters = ['memory', 'memory.usage', 'cpu', 'cpu_util'];

      interestingMeters.forEach((m, i) => {
        const meter = _.find(instance.stats, {meter: m});

        if(meter){
          
          statsContainer.append('text')
          .attr({
            y: 55 + (i * 15),
            x: serviceTopologyConfig.instance.margin,
            opacity: 0
          })
          .text(`${meter.description}: ${Math.round(meter.value)} ${meter.unit}`)
          .transition()
          .duration(serviceTopologyConfig.duration)
          .attr({
            opacity: 1
          });
        }

      });

      if(instance.container){
        // draw container
        drawContainer(statsContainer, instance.container);
      }

    };

    this.drawInstances = (container, instances) => {
      
      // TODO check for stats field in instance and draw popup

      let {width, height} = container.node().getBoundingClientRect();

      let elements = container.selectAll('.instances')
      .data(instances, d => angular.isString(d.d3Id) ? d.d3Id : d.d3Id = `instance-${++instanceId}`)

      var instanceContainer = elements.enter().append('g');

      instanceContainer
      .attr({
        transform: `translate(${width / 2}, ${ height / 2})`,
        class: d => `instance ${d.selected ? 'active' : ''} ${getInstanceStatusColor(d)}`,
      })
      .transition()
      .duration(serviceTopologyConfig.duration)
      .attr({
        transform: (d, i) => `translate(${RackHelper.getInstancePosition(i)})`
      });

      instanceContainer.append('rect')
      .attr({
        width: 0,
        height: 0
      })
      .transition()
      .duration(serviceTopologyConfig.duration)
      .attr({
        width: serviceTopologyConfig.instance.width,
        height: serviceTopologyConfig.instance.height
      });

      instanceContainer.append('text')
      .attr({
        'text-anchor': 'middle',
        y: 23, //FIXME
        x: 40, //FIXME
        opacity: 0
      })
      .text(d => formatInstanceName(d.humanReadableName))
      .transition()
      .duration(serviceTopologyConfig.duration)
      .attr({
        opacity: 1
      });

      // if stats are attached and instance is active,
      // draw stats
      instanceContainer.each(function(instance, i){

        const container = d3.select(this);

        if(angular.isDefined(instance.stats) && instance.selected){
          showInstanceStats(container, instance, i);
        }
      });

      // instanceContainer
      // .on('click', function(d){
      //   console.log(`Draw vignette with stats for instance: ${d.name}`);
      // });
    };

    this.addPhisical = (nodes) => {

      nodes.select('rect').remove();
      nodes.select('text').remove();

      nodes.append('rect')
      .attr(serviceTopologyConfig.square);

      nodes.append('text')
      .attr({
        'text-anchor': 'middle',
        y: serviceTopologyConfig.square.y - 10
      })
      .text(d => {
        return d.name || d.humanReadableName
      });
    }

    this.addDevice = (nodes) => {
      nodes.append('circle')
      .attr(serviceTopologyConfig.circle);

      nodes.append('text')
      .attr({
        'text-anchor': 'end',
        x: - serviceTopologyConfig.circle.r - 10,
        y: serviceTopologyConfig.circle.r / 2
      })
      .text(d => d.name || d.mac); 
    }
  });
})();
