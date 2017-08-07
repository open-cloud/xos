
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
    .directive('elanMap', function(){
      return {
        restrict: 'E',
        scope: {
          elan: '='
        },
        bindToController: true,
        controllerAs: 'vm',
        template: '',
        controller: function($element, $scope, $rootScope, $timeout,  _, cordIcons){
          const el = $element[0];
          var node, projection;
          $scope.$watch(() => this.elan, (elan) => {
            if(elan){
              $timeout(() => {
                draw(angular.copy(elan));
              }, 500)
            }
          }, true);

          // set force layout params
          var force = d3.layout.force();

          // DRAW US MAP
          const drawMap = () => {
            projection = d3.geo
              // .albersUsa()
              .mercator()
              .center([-122.2, 37.6])
              .scale(28000)
              .translate([el.clientWidth / 2, el.clientHeight / 2]);

            var path = d3.geo.path()
              .projection(projection);

            var map = d3.select(el).append('svg')
              .attr('id', 'map')
              .attr('width', el.clientWidth)
              .attr('height', el.clientHeight);

            d3.json('/js/json/bayarea.json', function(error, ba) {
              if (error) {
                throw new Error(error);
              };

              //bind feature data to the map
              map.selectAll('.subunit')
              .data(topojson.feature(ba, ba.objects.bayareaGEO).features)
              .enter().append('path')
              .attr('class', function(d, i) {
                return 'subunit ' + `_${i}`;
              })
              .attr('d', path);


            });
          };
          // END MAP

          const draw = (elan) => {
            if (!elan[0]){
              return;
            }
            // set size values
            force
              .size([el.clientWidth, el.clientHeight])
              .charge(-20)
              .chargeDistance(200)
              // .linkDistance(80)
              .linkStrength(0.1);

            // clean svg
            angular.element(el).children().remove();
            drawMap();

            // create svg elements
            const svg = d3.select(el)
              .append('svg')
              .style('width', `${el.clientWidth}px`)
              .style('height', `${el.clientHeight}px`)


            var nodes = [];
            var links = [];
            var d3id = 0;
            var unis_i = 0;
            var latlng_val, lat_val, lng_val;

            // cicle trough E-LINE and create nodes/links
            _.forEach(elan, (eline) => {

                let isOnMap = _.find(nodes, {id: eline.uni1.pid});

                if(!isOnMap){
                  eline.uni1.fixed = true;
                  try {

                    //convert latlng value into array for eline.uni1
                    var uni1_latlng = eline.uni1.latlng;
                    if (typeof uni1_latlng === 'string' || uni1_latlng instanceof String){
                        latlng_val = eline.uni1.latlng;
                        lat_val = latlng_val.substring(1, latlng_val.indexOf(',') - 1);
                        lat_val = lat_val.trim();
                        lng_val = latlng_val.substring(latlng_val.indexOf(',') + 1, latlng_val.length - 1);
                        lng_val = lng_val.trim()
                        eline.uni1.latlng = [lat_val, lng_val];
                    }

                    let ps = projection([eline.uni1.latlng[0], eline.uni1.latlng[1]]);
                    eline.uni1.x = ps[0];
                    eline.uni1.y = ps[1];
                    eline.uni1.pid = eline.uni1.pid || d3id++;
                    nodes.push(eline.uni1)
                  }
                  catch(e){
                    throw new Error(e);
                  }
                }
                else {
                  eline.uni1.pid = isOnMap.id;
                }

                isOnMap = _.find(nodes, {id: eline.uni2.pid});
                if(!isOnMap){
                  eline.uni2.fixed = true;
                  try {

                    //convert latlng value into array for eline.uni2
                    var uni2_latlng = eline.uni2.latlng;
                    if (typeof uni2_latlng === 'string' || uni2_latlng instanceof String){
                        latlng_val = eline.uni2.latlng;
                        lat_val = latlng_val.substring(1, latlng_val.indexOf(',') - 1);
                        lat_val = lat_val.trim();
                        lng_val = latlng_val.substring(latlng_val.indexOf(',') + 1, latlng_val.length - 1);
                        lng_val = lng_val.trim()
                        eline.uni2.latlng = [lat_val, lng_val];
                    }

                    let ps = projection([eline.uni2.latlng[0], eline.uni2.latlng[1]]);
                    eline.uni2.x = ps[0];
                    eline.uni2.y = ps[1];
                    eline.uni2.pid = eline.uni2.pid || d3id++;
                    nodes.push(eline.uni2)
                  }
                  catch(e){
                    throw new Error(e);
                  }
                }
                else {
                  eline.uni2.pid = isOnMap.id;
                }

              links.push({
                source: _.findIndex(nodes, eline.uni1),
                target: _.findIndex(nodes, eline.uni2),
                value: 1
              });

            });

            // start force layout
            force
              .nodes(nodes)
              .links(links)
              .start();

            // draw links
            var link = svg.selectAll('.link')
              .data(links)
              .enter().append('line')
              .attr({
                class: 'link',
              });

            //draw nodes
            node = svg.selectAll('.node')
              .data(nodes)
              .enter()
              .append('g', d => d.scaEthFppUniN.interfaceCfgIdentifier)
              .attr({
                class: d => `node ${d.type ? d.type : 'uni'}`
              });

            node.append('rect')
              .attr({
                class: d => d.type ? d.type : 'uni',
                width: 24,
                height: 24,
                x: -12,
                y: -12
              });

            node.append('path')
              .attr({
                d: cordIcons.cordLogo,
                transform: 'translate(-10, -10),scale(0.18)'
              });

            node.append('text')
              .attr({
                x: 0,
                y: 25,
                'text-anchor': 'middle'
              })
              .text(d => {
                return d.pid
              });


            force.on('tick', function() {
              link
                .attr('x1', function(d) { return d.source.x; })
                .attr('y1', function(d) { return d.source.y; })
                .attr('x2', function(d) { return d.target.x; })
                .attr('y2', function(d) { return d.target.y; });

              node.attr('transform', (d) => `translate(${d.x},${d.y})`);
            });
          };

        }
      }
    });
})();

