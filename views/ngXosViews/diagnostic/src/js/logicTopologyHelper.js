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
      .projection(d => {
        return [d.x, d.y];
      });

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
  });

}());