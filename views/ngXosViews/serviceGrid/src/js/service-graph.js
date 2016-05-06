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
      controller: function(){

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
