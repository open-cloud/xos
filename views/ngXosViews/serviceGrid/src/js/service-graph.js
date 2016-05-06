(function () {
  'use strict';

  angular.module('xos.serviceGrid')
  .directive('serviceGraph', function(){
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/service-graph.tpl.html',
      controller: function($element, GraphService){

        let svg;
        let el = $element[0];
        let node;
        let link;

        const tick = (e) => {
          // Push different nodes in different directions for clustering.
          
          node
            // .attr('cx', d => d.x)
            //   .attr('cy', d => d.y)
              .attr({
                transform: d => `translate(${d.x}, ${d.y})`
              });
          
          link.attr('x1', d => d.source.x)
              .attr('y1', d => d.source.y)
              .attr('x2', d => d.target.x)
              .attr('y2', d => d.target.y);
        }

        GraphService.loadCoarseData()
        .then((res) => {

          // build links
          res.tenants = res.tenants.map(t => {
            return {
              source: t.provider_service,
              target: t.subscriber_service
            }
          });

          // add xos as a node
          res.services.push({
            name: 'XOS',
            class: 'xos',
            x: el.clientWidth / 2,
            y: el.clientHeight / 2,
            fixed: true
          })

          handleSvg(el);

          var force = d3.layout.force()
            .nodes(res.services)
            .links(res.tenants)
            .charge(-1060)
            .gravity(0.1)
            .linkDistance(200)
            .size([el.clientWidth, el.clientHeight])
            .on('tick', tick)
            .start();

          link = svg.selectAll('.link')
          .data(res.tenants).enter().insert('line')
                .attr('class', 'link');

          node = svg.selectAll('.node')
            .data(res.services)
            .enter().append('g')
            .call(force.drag)
            .on("mousedown", function() { d3.event.stopPropagation(); });

          node.append('circle')
            .attr({
              class: d => `node ${d.class || ''}`,
              r: 10
            });

          node.append('text')
            .attr({
              'text-anchor': 'middle'
            })
            .text(d => d.name)

          node.select('circle')
            .attr({
              r: function(d){
                let parent = d3.select(this).node().parentNode;
                let sib = d3.select(parent).select('text').node().getBBox()
                return (sib.width / 2) + 10
                
              }
            })

        })

        const handleSvg = (el) => {
          d3.select(el).select('svg').remove();

          svg = d3.select(el)
          .append('svg')
          .style('width', `${el.clientWidth}px`)
          .style('height', `${el.clientHeight}px`);
        }
      }
    };
  })
})();

// Draw services around xos and calculate coarse tenant as links

// var width = 960, height = 500;

// var fill = d3.scale.category10();

// var nodes = [
//   {id: 1},
//   {id: 2},
//   {id: 3},
//   {id: 4},
//   {id: 5}
// ];

// var links = [
//   {source: 1, target: 2},
//   {source: 2, target: 3}
// ];

// var svg = d3.select("body").append("svg")
//     .attr("width", width)
//     .attr("height", height);

// var force = d3.layout.force()
//     .nodes(nodes)
//     .links(links)
//     .charge(-8*12)
//     .gravity(0.1)
//     .size([width, height])
//     .on("tick", tick)
//     .start();

// svg.append('circle')
// .attr({
//   "class": "xos",
//   r: 20,
//   cx: () => width / 2,
//   cy: () => height / 2,
// })

// var node = svg.selectAll(".node")
//     .data(nodes)
//   .enter().append("circle")
//     .attr("class", "node")
//     .attr("cx", ({ x }) => x)
//     .attr("cy", ({ y }) => y)
//     .attr("r", 8)
//     .style("fill", ({}, index) => fill(index & 3))
//     .style("stroke", ({}, index) => d3.rgb(fill(index & 3)).darker(2))
//     .call(force.drag)
//     .on("mousedown", ({}) => d3.event.stopPropagation());

// var link = svg.selectAll(".link")
// .data(links).enter().insert("line")
//       .attr("class", "link");

// function tick(e) {
//   // Push different nodes in different directions for clustering.
  
//   node.attr("cx", function(d) { return d.x; })
//       .attr("cy", function(d) { return d.y; });
  
//   link.attr("x1", function(d) { return d.source.x; })
//       .attr("y1", function(d) { return d.source.y; })
//       .attr("x2", function(d) { return d.target.x; })
//       .attr("y2", function(d) { return d.target.y; });
// }
