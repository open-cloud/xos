'use strict';

angular.module('xos.mcordTopology', [
  'ngResource',
  'ngCookies',
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
.factory('_', $window => $window._)
.service('Traffic', function($http, $q){
  this.get = () => {
    var deferred = $q.defer();
    $http.get('videoLocal.txt')
    .then(res => {
      deferred.resolve(res.data);
    })
    .catch(e => {
      console.log(e);
      deferred.resolve(Math.random() * 10)
    });
    return deferred.promise;
  }
})
.directive('mCordTopology', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    template: '',
    controller: function($element, $interval, $rootScope, _, $http, TopologyElements, NodeDrawer, Traffic){

      const el = $element[0];

      let nodes = [];
      let links = [];
      let traffic = 0;
      let linkWidth = 1;
      let trafficCorrection = 5;

      const filterBBU = (instances) => {
        return _.filter(instances, i => i.name.indexOf("bbu") >= 0);
      };

      const filterOthers = (instances) => {
        return TopologyElements.fakedInstance;
      };

      // retrieving instances list
      const getData = () => {

        d3.select('svg')
          .style('width', `${el.clientWidth}px`)
          .style('height', `${el.clientHeight}px`);

        nodes = TopologyElements.nodes;
        links = TopologyElements.links;

        Traffic.get()
        .then((newTraffic) => {

          // calculating link size
          // it should change between 1 and 10
          if(!traffic){
            linkWidth = 2;
          }
          else if(newTraffic === traffic){
            linkWidth = linkWidth;
          }
          else{
            let delta = newTraffic - traffic;

            if(delta > 0){
              linkWidth = linkWidth + (delta / trafficCorrection);
            }
            else{
              linkWidth = linkWidth - ((delta * -1) / trafficCorrection);
            }

          }

          if(linkWidth < 0.2){
            linkWidth = 0.2
          };

          traffic = newTraffic;

          return $http.get('/api/core/xos/instances');
          // return XosApi.Instance_List_GET()
        })
        .then((instances) => {

          addBbuNodes(filterBBU(instances.data));
          addOtherNodes(filterOthers(instances.data));

          draw(svg, nodes, links);
        })
        .catch((e) => {
          throw new Error(e);
        });
      };

      const force = d3.layout.force();

      // create svg elements
      const svg = d3.select(el)
        .append('svg')
        .style('width', `${el.clientWidth}px`)
        .style('height', `${el.clientHeight}px`);

      const linkContainer = svg.append('g')
        .attr({
          class: 'link-container'
        });

      const nodeContainer = svg.append('g')
        .attr({
          class: 'node-container'
        });

      // replace human readable ids with d3 ids
      // NOTE now ids are not manatined on update...
      const buildLinks = (links, nodes) => {
        return links.map((l) => {

          console.log(_.find);
          let source = _.findIndex(nodes, {id: l.source});
          let target = _.findIndex(nodes, {id: l.target});
          // console.log(`link-${source}-${target}`, source, target);
          return {
            source: source,
            target: target,
            value: 1,
            id: `link-${source}-${target}`,
            type: l.source.indexOf('fabric') >= 0 ? 'big':'small'
          };

        });
      };

      // find fabric nodes and center horizontally
      const positionFabricNodes = (nodes) => {
        return _.map(nodes, n => {
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
            target: 'fabric4'
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

      let hStep, vStep;

      hStep = el.clientWidth / 3;
      vStep = el.clientHeight / 5;

      const draw = (svg, nodes, links) => {

        hStep = el.clientWidth / 3;
        vStep = el.clientHeight / 5;

        links = buildLinks(links, nodes);

        nodes = positionFabricNodes(nodes);

        console.log(nodes);
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


        const linkContainer = d3.select('.link-container');
        const nodeContainer = d3.select('.node-container');

        NodeDrawer.drawFabricBox(nodeContainer, hStep, vStep);

        // draw links
        var link = linkContainer.selectAll('.link')
          .data(links, d => d.id);
        
        link.enter().append('line')
          .attr({
            class: d => `link ${d.type}`,
            'stroke-width': linkWidth,
            id: d => d.id,
            opacity: 0
          })
          .transition()
          .duration(1000)
          .attr({
            opacity: 1
          });

        link
          .transition()
          .duration(1000)
          .attr({
            'stroke-width': linkWidth,
            opacity: 1
          });

        link.exit()
        .remove();

        //draw nodes
        var node = nodeContainer.selectAll('.node')
          .data(nodes, d => {
            return d.id
          });
        
        // append a group for any new node
        var enter = node.enter()
          .append('g', d => d.interfaceCfgIdentifier)
          .attr({
            class: d => `${d.type} node`,
            transform: d => `translate(${d.x}, ${d.y})`
          });

        // draw nodes
        NodeDrawer.drawBbus(enter.filter('.bbu'))
        NodeDrawer.drawRrus(enter.filter('.rru'))
        NodeDrawer.drawFabric(enter.filter('.fabric'))
        NodeDrawer.drawOthers(enter.filter(d => {
          console.log(d.type);
          return (
            d.type  === 'MME' ||
            d.type === 'SGW' ||
            d.type === 'PGW' ||
            d.type === 'Vid'
          )
        }));

        // remove nodes
        var exit = node.exit();

        NodeDrawer.removeElements(exit);

        force.on('tick', function() {
          link
            .attr('x1', d => d.source.x )
            .attr('y1', d => d.source.y )
            .attr('x2', d => d.target.x )
            .attr('y2', d => d.target.y );

          node.attr('transform', (d) => `translate(${d.x},${d.y})`);
        });
      };
      
      // $interval(() => {
      //   getData();
      // }, 3000);
      getData();

      
    }
  };
});
