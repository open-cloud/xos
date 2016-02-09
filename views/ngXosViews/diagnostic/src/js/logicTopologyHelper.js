(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .service('LogicTopologyHelper', function($window, $log, lodash, serviceTopologyConfig){

    var hStep, vStep;

    const createDevice = (container, device, xPos, yPos, target) => {

      const deviceGroup = container.append('g')
      .attr({
        class: 'device',
        transform: `translate(${xPos}, ${yPos})`
      });

      const deviceEl = deviceGroup.append('circle')
      .attr({
        r: serviceTopologyConfig.circle.radius
      });

      deviceGroup.append('text')
      .attr({
        x: - serviceTopologyConfig.circle.radius - 3,
        dy: '.35em',
        'text-anchor': 'end'
      })
      .text(device.name)

      const [deviceX, deviceY] = d3.transform(deviceEl.attr('transform')).translate;
      const [deviceGroupX, deviceGroupY] = d3.transform(deviceGroup.attr('transform')).translate;
      let [targetX, targetY] = d3.transform(target.attr('transform')).translate;

      targetX = targetX - deviceGroupX;
      targetY = targetY - deviceGroupY;

      console.log('Device: ' + deviceX, deviceY);
      console.log('Subscriber: ' + targetX, targetY);

      var diagonal = d3.svg.diagonal()
      .source({x: deviceX, y: deviceY})
      .target({x: targetX, y: targetY})
      // .projection(d => {
      //   return [d.y, d.x];
      // });

      deviceGroup
        .append('path')
        .attr('class', 'device-link')
        .attr('d', diagonal);
    }

    const createSubscriber = (container, subscriber, xPos, yPos) => {

      const subscriberGroup = container.append('g')
      .attr({
        class: 'subscriber',
        transform: `translate(${xPos * 2}, ${yPos})`
      });

      subscriberGroup.append('circle')
      .attr({
        r: serviceTopologyConfig.circle.radius
      });

      subscriberGroup.append('text')
      .attr({
        x: serviceTopologyConfig.circle.radius + 3,
        dy: '.35em',
        'text-anchor': 'start'
      })
      .text(subscriber.humanReadableName)

      // TODO
      // starting from the subscriber position, we should center
      // the device goup based on his own height
      // const deviceContainer = container.append('g')
      // .attr({
      //   class: 'devices-container',
      //   transform: `translate(${xPos}, ${yPos -(vStep / 2)})`
      // });

      angular.forEach(subscriber.devices, (device, j) => {
        createDevice(container, device, xPos, ((vStep / subscriber.devices.length) * j) + (yPos - vStep / 2), subscriberGroup);
      });
    }

    this.handleSubscribers = (svg, subscribers) => {

      // HACKY
      hStep = angular.element(svg[0])[0].clientWidth / 7;
      vStep = angular.element(svg[0])[0].clientHeight / (subscribers.length + 1);

      const container = svg.append('g')
      .attr({
        class: 'subscribers-container'
      });

      lodash.forEach(subscribers, (subscriber, i) => {
        createSubscriber(container, subscriber, hStep, vStep * (i + 1));
      })
    }

    var diagonal, nodes, links, i = 0, svgWidth, svgHeight, layout;

    const baseData = {
      name: 'Router',
      type: 'router',
      children: [
        {
          name: 'WAN',
          type: 'network',
          children: [
            {
              name: 'Rack',
              type: 'rack',
              children: [
                {
                  name: 'LAN',
                  type: 'network',
                  children: [] //subscribers goes here
                }
              ]
            }
          ]
        }
      ]
    };

    const computeLayout = (data) => {
      let nodes = layout.nodes(data);

      // Normalize for fixed-depth.
      nodes.forEach(function(d) {
        // position the child node horizontally
        const step = ((svgWidth - (serviceTopologyConfig.widthMargin * 2)) / 7);
        d.y = (6 - d.depth) * step;
      });

      let links = layout.links(nodes);
      console.log(nodes.length, links.length);
      return [nodes, links];
    };

    const drawNodes = (svg, nodes) => {
      // Update the nodes…
      var node = svg.selectAll('g.node')
      .data(nodes, d => {return d.id || (d.id = `tree-${i++}`)});

      // Enter any new nodes at the parent's previous position.
      var nodeEnter = node.enter().append('g')
      .attr({
        class: d => `node ${d.type}`,
        transform: `translate(${svgWidth / 2}, ${svgHeight / 2})`
      });

      nodeEnter.append('circle')
        .attr('r', 10)
        .style('fill', d => d._children ? 'lightsteelblue' : '#fff');

      nodeEnter.append('text')
        .attr({
          x: d => d.children ? serviceTopologyConfig.circle.selectedRadius + 3 : -serviceTopologyConfig.circle.selectedRadius - 3,
          dy: '.35em',
          transform: d => {
            if (d.children && d.parent){
              if(d.parent.x < d.x){
                return 'rotate(-30)';
              }
              return 'rotate(30)';
            }
          },
          'text-anchor': d => d.children ? 'start' : 'end'
        })
        .text(d => d.name);

      // Transition nodes to their new position.
      var nodeUpdate = node.transition()
        .duration(serviceTopologyConfig.duration)
        .attr({
          'transform': d => `translate(${d.y},${d.x})`
        });

      // TODO handle node remove
    };

    const drawLinks = (svg, links) => {

      diagonal = d3.svg.diagonal()
      .projection(d => [d.y, d.x]);

      // Update the links…
      var link = svg.selectAll('path.link')
        .data(links, d => {
          return d.target.id
        });

      // Enter any new links at the parent's previous position.
      link.enter().insert('path', 'g')
        .attr('class', d => `link ${d.target.type}`)
        .attr('d', function(d) {
          var o = {x: svgHeight / 2, y: svgWidth / 2};
          return diagonal({source: o, target: o});
        });

      // Transition links to their new position.
      link.transition()
        .duration(serviceTopologyConfig.duration)
        .attr('d', diagonal);
    };

    this.drawTree = (svg) => {
      

      svgWidth = svg.node().getBoundingClientRect().width;
      svgHeight = svg.node().getBoundingClientRect().height;

      const width = svgWidth - (serviceTopologyConfig.widthMargin * 2);
      const height = svgHeight - (serviceTopologyConfig.heightMargin * 2);

      layout = d3.layout.tree()
      .size([height, width]);

      // Compute the new tree layout.
      [nodes, links] = computeLayout(baseData);

      drawNodes(svg, nodes);
      drawLinks(svg, links);
      
    };

    this.addSubscribers = (svg, subscribers) => {

      console.log(subscribers);

      subscribers.map((subscriber) => {
        subscriber.children = subscriber.devices;
      });

      // add subscriber to data tree
      baseData.children[0].children[0].children[0].children = subscribers;

      console.log(baseData);

      [nodes, links] = computeLayout(baseData);

      drawNodes(svg, nodes);
      drawLinks(svg, links);
    }
  });

}());