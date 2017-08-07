
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


/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 6/28/16.
 */

(function () {
  'use strict';
  angular.module('xos.ecordTopology')
  .directive('serviceMap', function(){
    return {
      restrict: 'E',
      scope: {
        unis: '=',
        services: '='
      },
      bindToController: true,
      controllerAs: 'vm',
      template: '',
      controller: function($element, $scope, $rootScope, $timeout, $log, cordIcons){
        const el = $element[0];
        const layout = d3.layout.tree();
        let duration = 500;
        let margin = 40;

        // count the mas depth of an object
        const depthOf = (obj) => {
          var depth = 0;
          if (obj.children) {
            obj.children.forEach(function (d) {
              var tmpDepth = depthOf(d);
              if (tmpDepth > depth) {
                depth = tmpDepth
              }
            })
          }
          return 1 + depth
        };

        // create svg elements
        const svg = d3.select(el)
          .append('svg')
          .style('width', `${el.clientWidth}px`)
          .style('height', `${el.clientHeight}px`)

        var diagonal = d3.svg.diagonal()
          .projection(function(d) { return [d.y, d.x]; });

        let i = 0;
        const update = (tree) => {

          let maxDepth = depthOf(tree);

          layout
            .size([el.clientHeight, el.clientWidth]);

          var nodes = layout.nodes(tree);
          var links = layout.links(nodes);

          const step = ((el.clientWidth - margin) / (maxDepth - 1));
          // Normalize for fixed-depth.
          nodes.forEach(function(d, i) {
            if(i === 0){
              d.y = margin;
            }
            else{
              d.y = d.depth * step;
            }
          });

          // Update the nodes…
          var node = svg.selectAll('g.node')
            .data(nodes, (d) =>  {
              return d.id || (d.id = ++i)
            });


          // Enter any new nodes at the parent's previous position.
          var nodeEnter = node.enter().append('g')
            .attr({
              'class': d => `node ${d.type}`,
              id: d => d.id
            })
            .attr('transform', () => `translate(${el.clientWidth / 2}, 50)`);

          nodeEnter.append('rect')
            .attr({
              class: d => d.type,
              width: 24,
              height: 24,
              x: -12,
              y: -12
            });

          // unis
          nodeEnter.filter('.uni')
            .append('path')
            .attr({
              d: cordIcons.cordLogo,
              transform: 'translate(-10, -10),scale(0.18)'
            });

          // services
          nodeEnter.filter('.service')
            .append('path')
            .attr({
              d: cordIcons.service,
              transform: 'translate(-12, -12)'
            });

          nodeEnter.append('text')
            .attr({
              'text-anchor': 'middle',
              x: 0,
              y: 25
            })
            .text(d => {
              return d.name
            });

          // Transition exiting nodes to the parent's new position.
          var nodeExit = node.exit().transition()
            .duration(duration)
            .remove();

          nodeExit.select('circle')
            .attr('r', 1e-6);

          nodeExit.select('text')
            .style('fill-opacity', 1e-6);

          var nodeUpdate = node.transition()
            .duration(duration)
            .attr('transform', (d) => `translate(${d.y},${d.x})`);

          // Update the links…
          var link = svg.selectAll('path.link')
            .data(links, function(d) { return d.target.id; });

          // Enter any new links at the parent's previous position.
          link.enter().insert('path', 'g')
            .attr('class', 'link')
            .attr('d', function(d) {
              var o = {x: d.source.x, y: d.source.y};
              return diagonal({source: o, target: o});
            });

          // Transition links to their new position.
          link.transition()
            .duration(duration)
            .attr('d', diagonal);

          // Transition exiting nodes to the parent's new position.
          link.exit().transition()
            .duration(duration)
            .attr('d', function(d) {
              var o = {x: d.source.x, y: d.source.y};
              return diagonal({source: o, target: o});
            })
            .remove();

          // Stash the old positions for transition.
          nodes.forEach(function(d) {
            d.x0 = d.x;
            d.y0 = d.y;
          });
        };

        // format uni in the tree layout shape
        this.formatUni = (unis) => {
          return unis.reduce((list, item, i) => {
            list.push({
              name: item.scaEthFppUniN.name,
              children: [],
              id: `uni-${i}`
            });
            return list;
          }, [])
          return unis;
        }

        // add active services
        this.addServices = (services, unis) => {

          let list = [unis[0], ...services, unis[1]];


          const addChildR = (base, list) => {

            if(list.length === 0){
              return [];
            }

            let el = list.shift();

            let n = {
              name: el.name || el.label,
              type: el.name ? 'uni':'service',
              children: addChildR(el, list),
              id: el.id
            };

            return [n];
          };

          let tree = addChildR({}, list);

          return tree[0];
        };

        $scope.$watch(() => this.services, (s) => {
          if(s && this.unis){
            update(this.addServices(s, this.formatUni(this.unis)))
          }
        }, true)
      }
    };
  });
})();

