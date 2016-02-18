'use strict';

angular.module('xos.mcordTopology', [
  'ngResource',
  'ngCookies',
  'ngLodash',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('topology', {
    url: '/',
    template: '<m-cord-topology></m-cord-topology>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('mCordTopology', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    template: '',
    controller: function($element, $window, XosApi, lodash, TopologyElements, NodeDrawer){

      const el = $element[0];

      let nodes = TopologyElements.nodes;
      let links = TopologyElements.links;

      const filterBBU = (instances) => {
        return lodash.filter(instances, i => i.name.indexOf('BBU') >= 0);
      };

      const filterOthers = (instances) => {
        return lodash.filter(instances, i => {
          return (i.name.indexOf('MME') >= 0)
          || (i.name.indexOf('SGW') >= 0)
          || (i.name.indexOf('PGW') >= 0)
        });
      };

      // retrieving instances list
      XosApi.Instance_List_GET()
      .then((instances) => {
        addBbuNodes(filterBBU(instances));
        addOtherNodes(filterOthers(instances));
        draw(svg, nodes, links);
      })
      .catch((e) => {
        throw new Error(e);
      });

      const force = d3.layout.force();

      // create svg elements
      const svg = d3.select(el)
        .append('svg')
        .style('width', `${el.clientWidth}px`)
        .style('height', `${el.clientHeight}px`);


      let hStep = el.clientWidth / 3;
      let vStep = el.clientHeight / 5;

      // replace human readable ids with d3 ids
      const buildLinks = (links, nodes) => {
        return links.map((l) => {
          let source = lodash.findIndex(nodes, {id: l.source});
          let target = lodash.findIndex(nodes, {id: l.target});
          return {
            source: source,
            target: target,
            value: 1
          };

        });
      };

      // find fabric nodes and center horizontally
      const positionFabricNodes = (nodes) => {
        return lodash.map(nodes, n => {
          if(n.type !== 'fabric'){
            return n;
          }

          n.x = n.x * hStep;
          n.y = n.y * vStep;

          return n;
        });
      };

      const addBbuNodes = (instances) => {

        // calculate bbu hStep
        let bbuHStep = ((el.clientWidth / 2) / (instances.length + 1));

        // create nodes
        let bbuNodes = instances.map((n, i) => {
          return {
            type: 'bbu',
            name: n.name,
            id: `bbu-${n.id}`,
            fixed: true,
            y: vStep * 3,
            x: bbuHStep * (i + 1)
          };
        });

        // create links
        let bbuLinks = bbuNodes.map(n => {
          return {
            source: n.id,
            target: 'fabric2'
          };
        });

        // fake RRU nodes and links
        instances.forEach((n, i) => {
          bbuNodes.push({
            type: 'rru',
            name: 'rru',
            id: `rru-${n.id}`,
            fixed: true,
            y: vStep * 4,
            x: bbuHStep * (i + 1)
          });

          bbuLinks.push({
            source: `rru-${n.id}`,
            target: `bbu-${n.id}`
          });
        })

        nodes = nodes.concat(bbuNodes);
        links = links.concat(bbuLinks);
      };

      // add MME, PGW, SGW nodes
      const addOtherNodes = (instances) => {
        let hStep = ((el.clientWidth / 2) / (instances.length + 1));

        // create nodes
        let otherNodes = instances.map((n, i) => {
          return {
            type: n.name.substring(0, 3),
            name: n.name,
            id: `${n.name.substring(0, 3)}-${n.id}`,
            fixed: true,
            y: vStep * 3,
            x: (el.clientWidth / 2) + (hStep * (i + 1))
          };
        });

        // create links
        let otherLinks = otherNodes.map(n => {
          return {
            source: n.id,
            target: 'fabric4'
          };
        });

        nodes = nodes.concat(otherNodes);
        links = links.concat(otherLinks);
      }

      // NOTE nodes get dublicated
      const draw = (svg, nodes, links) => {

        links = buildLinks(links, nodes);

        nodes = positionFabricNodes(nodes);

        // start force layout
        force
          .nodes(nodes)
          .links(links)
          .size([el.clientWidth, el.clientHeight])
          .charge(-20)
          .chargeDistance(200)
          .linkDistance(80)
          .linkStrength(0.1)
          .start();

        // draw links
        var link = svg.selectAll('.link')
          .data(links)
          .enter().append('line')
          .attr({
            class: 'link',
          });

        //draw nodes
        var node = svg.selectAll('.node')
          .data(nodes, d => {
            return d.id
          });
        
        // append a group for any new node
        var enter = node.enter()
          .append('g', d => d.interfaceCfgIdentifier)
          .attr({
            class: d => d.type,
            transform: d => `translate(${d.x}, ${d.y})`
          });

        // draw nodes
        NodeDrawer.drawBbus(node.filter('.bbu'))
        NodeDrawer.drawRrus(node.filter('.rru'))
        NodeDrawer.drawFabric(node.filter('.fabric'))
        NodeDrawer.drawOthers(node.filter(d => {
          return (
            d.type  === 'MME' ||
            d.type === 'SGW' ||
            d.type === 'PGW'
          )
        }));

        force.on('tick', function() {
          link
            .attr('x1', d => d.source.x )
            .attr('y1', d => d.source.y )
            .attr('x2', d => d.target.x )
            .attr('y2', d => d.target.y );

          node.attr('transform', (d) => `translate(${d.x},${d.y})`);
        });
      };
      
      // draw(svg, TopologyElements.nodes, TopologyElements.links);
    }
  };
});