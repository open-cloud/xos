
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


(function () {
  'use strict';

  angular.module('xos.diagnostic')
  .directive('serviceTopology', function(){
    return {
      restrict: 'E',
      scope: {
        serviceChain: '='
      },
      bindToController: true,
      controllerAs: 'vm',
      template: '',
      controller: function($element, $window, $scope, d3, serviceTopologyConfig, ServiceRelation, Instances, Subscribers, ServiceTopologyHelper){

        const el = $element[0];

        d3.select(window)
        .on('resize.service', () => {
          draw(this.serviceChain);
        });

        var root, svg;

        const draw = (tree) => {

          if(!tree){
            console.error('Tree is missing');
            return;
          }

          // TODO update instead clear and redraw

          // clean
          d3.select($element[0]).select('svg').remove();


          const width = el.clientWidth - (serviceTopologyConfig.widthMargin * 2);
          const height = el.clientHeight - (serviceTopologyConfig.heightMargin * 2);

          const treeLayout = d3.layout.tree()
            .size([height, width]);

          svg = d3.select($element[0])
            .append('svg')
            .style('width', `${el.clientWidth}px`)
            .style('height', `${el.clientHeight}px`)

          const treeContainer = svg.append('g')
            .attr('transform', `translate(${serviceTopologyConfig.widthMargin * 2},${serviceTopologyConfig.heightMargin})`);

          root = tree;
          root.x0 = height / 2;
          root.y0 = width / 2;

          // ServiceTopologyHelper.drawLegend(svg);
          ServiceTopologyHelper.updateTree(treeContainer, treeLayout, root, el);
        };
        
        $scope.$watch(() => this.serviceChain, (chain) => {
          if(angular.isDefined(chain)){
            draw(chain);
          }
        });
      }
    }
  });

}());