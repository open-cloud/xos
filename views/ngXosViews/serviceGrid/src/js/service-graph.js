(function () {
  'use strict';

  angular.module('xos.serviceGrid')
  .service('Graph', function($q, Tenants, Services, Subscribers){

    let tenancyGraph = new graphlib.Graph();
    let cached = false;

    const buildGraph = () => {

      let deferred = $q.defer();

      $q.all([
        Tenants.query().$promise,
        Services.query().$promise,
        Subscribers.query().$promise
      ])
      .then((res) => {
        let [tenants, services, subscribers] = res;
        // adding service nodes
        services.forEach(s => tenancyGraph.setNode(s.id, angular.extend(s, {type: 'service'})));


        // coarse tenant
        tenants.filter(t => t.subscriber_service && t.provider_service)
          .forEach(t => tenancyGraph.setEdge(t.subscriber_service, t.provider_service, t, t.name));

        // fine grain tenant
        // adding subscribers as nodes (to build fine grain graph)
        // subscribers.forEach(s => tenancyGraph.setNode(`sub-${s.id}`, angular.extend(s, {type: 'subscriber'})));
        // TODO
        // - Find tenant that start from a subscriber
        // - Follow the chain: from the first tenant follow where subscriber_tenant = tenant_id untill we cannot find any more tenant
        // tenants.filter(t => t.subscriber_root && t.provider_service)
        // .forEach(t => tenancyGraph.setEdge(`sub-${t.subscriber_root}`, t.provider_service, t, t.name));
        
        deferred.resolve(tenancyGraph);
      });

      return deferred.promise;
    };

    this.getGraph = () => {
      let deferred = $q.defer();

      if(cached){
        deferred.resolve(tenancyGraph);
      }
      else {
        buildGraph()
        .then((res) => {
          cached = true;
          deferred.resolve(res);
        })
        .catch(console.log);
      }

      return {$promise: deferred.promise};
    };

  })
  .directive('serviceGraph', function(){
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/service-graph.tpl.html',
      controller: function($scope, $element, GraphService, Graph, ToscaEncoder){

        let svg;
        let el = $element[0];
        let node, nodes;
        let link, links;
        const _this = this;

        this.panelConfig = {
          position: 'right'
        };

        // find position for link labels
        const xpos = (source, target) => {
          if (target.x > source.x) {
            return (source.x + (target.x - source.x)/2); }
          else {
            return (target.x + (source.x - target.x)/2); }
        }

        const ypos = (source, target) => {
          if (target.y > source.y) {
            return Math.round(source.y + (target.y - source.y)/2);
          }
          else {
            return Math.round(target.y + (source.y - target.y)/2); }
        }

        // animate node and links in the correct place
        const tick = () => {
          node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y)
            .attr({
              transform: d => `translate(${d.x}, ${d.y})`
            });
          
          svg.selectAll('.link')
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => getTargetNodeCircumferencePoint(d)[0])
            .attr('y2', d => getTargetNodeCircumferencePoint(d)[1]);

          svg.selectAll('.link-text')
            .attr('x', d => xpos(d.source, {x: getTargetNodeCircumferencePoint(d)[0], y: getTargetNodeCircumferencePoint(d)[1]}))
            .attr('y', d => ypos(d.source, {x: getTargetNodeCircumferencePoint(d)[0], y: getTargetNodeCircumferencePoint(d)[1]}))
            .attr('transform', d => {
              let x = xpos(d.source, {x: getTargetNodeCircumferencePoint(d)[0], y: getTargetNodeCircumferencePoint(d)[1]});
              let y = ypos(d.source, {x: getTargetNodeCircumferencePoint(d)[0], y: getTargetNodeCircumferencePoint(d)[1]});
              return `rotate(-30, ${x}, ${y})`;
            });
        };

        var chainCount = 1;
        var spareCount = 1;

        const getNodePosition = (n, graph, chainElements) => {
          let node =  graph.node(n);
          const step = el.clientWidth / (chainElements + 1);

          if(graph.nodeEdges(n).length > 0){
            let pos = {
              y: el.clientHeight / 4,
              x: step * chainCount,
              fixed: true
            };
            angular.extend(node, pos);
            chainCount = chainCount + 1;
          }
          else {
            let pos = {
              y: (el.clientHeight / 2) + (el.clientHeight / 4),
              x: (step + step / 2) * spareCount,
              fixed: true
            };
            angular.extend(node, pos);
            spareCount = spareCount + 1;
          }
          return node;
        };

        Graph.getGraph().$promise
        .then((graph) => {

          // build links
          links = graph.edges().map(e => {
            return {
              source: graph.node(e.v),
              target: graph.node(e.w),
              tenant: graph.edge(e)
            }
          });
          
          // check how many nodes are connected
          // let longerGraph = graphlib.alg.components(graph).filter(g => g.length > 1);
          const longerGraph = graphlib.alg.components(graph).reduce(function (a, b) { return a.length > b.length ? a : b; }).length;

          nodes = graph.nodes().reverse().map(n => getNodePosition(n, graph, longerGraph));

          handleSvg(el);
          defineArrows();

          var force = d3.layout.force()
            .nodes(nodes)
            .links(links)
            .charge(-1060)
            .gravity(0.1)
            .linkDistance(200)
            .size([el.clientWidth, el.clientHeight])
            .on('tick', tick)
            .start();

          link = svg.selectAll('.link-container')
            .data(links).enter().insert('g')
            .attr('class', 'link-container');

          link.insert('line')
            .attr('class', 'link')
            .attr('marker-end', 'url(#arrow)');

          var linkText = svg.selectAll('.link-container')
            .data(force.links())
            .insert('text')
            .attr({
              class: 'link-text',
              'text-anchor': 'start'
            })
            .text(d => `${d.tenant.humanReadableName}`)

          node = svg.selectAll('.node')
            .data(nodes)
            .enter().append('g')
            .call(force.drag)
            .on('mousedown', function(d) {
              $scope.$apply(() => {
                if(d.name === 'XOS'){
                  return;
                }
                _this.panelShow = true;
                let status = parseInt(d.backend_status.match(/^[0-9]/)[0]);
                console.log(status);
                switch(status){
                  case 0:
                    d.icon = 'time';
                    break;
                  case 1:
                    d.icon = 'ok';
                    break;
                  case 2:
                    d.icon = 'remove';
                    break;
                }
                _this.selectedNode = d;
              });
              d3.event.stopPropagation();
            });

          node.append('circle')
            .attr({
              class: d => `node ${d.type || ''}`,
              r: 10
            });

          node.append('text')
            .attr({
              'text-anchor': 'middle',
              'alignment-baseline': 'middle'
            })
            .text(d => d.humanReadableName || d.name);

          // scale the node to fit the contained text
          node.select('circle')
            .attr({
              r: function(d){
                const parent = d3.select(this).node().parentNode;
                const sib = d3.select(parent).select('text').node().getBBox();
                const radius = (sib.width / 2) + 10;

                // add radius as node attribute
                d.nodeWidth = radius * 2;
                return radius;
              }
            })

        });

        const handleSvg = (el) => {
          d3.select(el).select('svg').remove();

          svg = d3.select(el)
          .append('svg')
          .style('width', `${el.clientWidth}px`)
          .style('height', `${el.clientHeight}px`);
        };

        const defineArrows = () => {
          svg.append('svg:defs').selectAll('marker')
          .data(['arrow'])      // Different link/path types can be defined here
          .enter().append('svg:marker')    // This section adds in the arrows
          .attr('id', String)
          .attr('viewBox', '0 -5 10 10')
          .attr('refX', 10)
          .attr('refY', 0)
          .attr('markerWidth', 6)
          .attr('markerHeight', 6)
          .attr('orient', 'auto')
          .attr('class', 'link-arrow')
          .append('svg:path')
          .attr('d', 'M0,-5L10,0L0,5');
        };

        const getTargetNodeCircumferencePoint = d => {
          const radius = d.target.nodeWidth / 2; // nodeWidth is just a custom attribute I calculate during the creation of the nodes depending on the node width
          const dx = d.target.x - d.source.x;
          const dy = d.target.y - d.source.y;
          const gamma = Math.atan2(dy, dx); // Math.atan2 returns the angle in the correct quadrant as opposed to Math.atan

          const tx = d.target.x - (Math.cos(gamma) * radius);
          const ty = d.target.y - (Math.sin(gamma) * radius);

          return [tx, ty];
        };

        this.exportToTosca = (service) => {
          ToscaEncoder.serviceToTosca(service);
        }
      }
    };
  })
})();