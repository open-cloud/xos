(function () {
  'use strict';

  angular.module('xos.mcord-slicing')
  .directive('slicingTopo', function(){
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/slicing-topo.tpl.html',
      controller: function($element, SliceGraph, McordSlicingTopo, _, NodePositioner, FormHandler, mCordSlicingIcons){

        let svg;
        let nodes, links;
        let nodeGroup, linkGroup, formGroup;
        let dragLine, dragStartNode, dragEndNode, selectedLink;
        let selectedNode, nodeSiblings;

        var t = d3.transition()
          .duration(500);

        this.activeSlices = [];

        const resetDragInfo = () => {
          // reset drag nodes
          dragStartNode = null;
          dragEndNode = null;

          // hide dragLine
          dragLine
            .classed('hidden', true);
        };

        McordSlicingTopo.query().$promise
        .then((topology) => {
          NodePositioner.storeEl($element[0]);
          handleSvg($element[0]);
          SliceGraph.buildGraph(topology);
          _nodes = SliceGraph.positionGraph($element[0]);
          _links = SliceGraph.getGraphLinks(_nodes);
          drawGraph();
        })
        .catch((e) => {
          throw new Error(e);
        });

        const handleSvg = (el) => {
          this.el = el;
          d3.select(el).select('svg').remove();

          svg = d3.select(el)
          .append('svg')
          .style('width', `${el.clientWidth}px`)
          .style('height', `${el.clientHeight}px`);

          linkGroup = svg.append('g')
            .attr({
              class: 'link-group'
            });

          nodeGroup = svg.append('g')
            .attr({
              class: 'node-group'
            });

          formGroup = d3.select(el)
            .append('div')
            .attr({
              class: 'form-container'
            });

          // line displayed when dragging nodes
          dragLine = svg.append('svg:path')
            .attr('class', 'dragline hidden')
            .attr('d', 'M0,0L0,0');
        };

        const tick = () => {

          // svg.selectAll('.node')
          // .attr({
          //   y: (n) => {
          //     console.log(n.y);
          //     return n.y;
          //   }
          // });

          svg.selectAll('.link')
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        };

        // prepare the data to show all slices
        let _nodes = [];
        let _links = [];

        // attach slice details
        const attachSliceDetails = n => {
          let [newNodes, newLinks] = SliceGraph.getSliceDetail(n);
          _nodes = _nodes.concat(newNodes);
          _links = _links.concat(newLinks);
          drawGraph();
        };

        // remove slice detail
        const removeSliceDetails = sliceId => {

          SliceGraph.removeActiveSlice(sliceId);

          // if the selected node is part of the slice I'm closing
          // deselect the node
          if(selectedNode && selectedNode.sliceId === sliceId){
            selectedNode = null;
            nodeSiblings = null;
          }

          // remove control plane nodes related to this slice
          _nodes = _.filter(_nodes, n => {
            if(n.sliceId === sliceId && (n.plane === 'control' || n.type === 'button')){
              // if I remove the node check that there is no form attached
              FormHandler.removeFormByParentNode(n, linkGroup, formGroup);
              return false;
            }
            return true;
          });

          // remove sliceId from data plane element
          _nodes = _.map(_nodes, n => {
            if(n.sliceId === sliceId){
              delete n.sliceId;
            }
            return n;
          });

          // remove control plane links related to this slice
          _links = _.filter(_links, l => {
            if(_.findIndex(_nodes, {id: l.data.source}) === -1){
              return false;
            }
            if(_.findIndex(_nodes, {id: l.data.target}) === -1){
              return false;
            }
            return true;
          });
          drawGraph();
        };

        const deleteLink = linkId => {
          // TODO
          // [ ] delete from graphlib
          // [ ] delete from backend
          console.log(_links);
          _.remove(_links, (l) => {
            return l.data.id === linkId;
          });
          console.log(_links);
          drawGraph();
        };

        const expandNode = (n) => {
          console.log('exp', n);
          resetDragInfo();
          const sliceComponents = ['ran-ru', 'ran-cu', 'pgw', 'sgw'];
          if(sliceComponents.indexOf(n.type) > -1 && n.plane === 'data' && !n.sliceId){
            attachSliceDetails(n);
          }
          else if (n.type === 'button'){
            removeSliceDetails(n.sliceId);
          }
          else if (!n.formAttached && n.model){
            n.formAttached = true;
            FormHandler.drawForm(n, linkGroup, formGroup);
          }
          else if (n.formAttached){
            n.formAttached = false;
            FormHandler.removeFormByParentNode(n, linkGroup, formGroup);
          }
        };

        const selectNextNode = () => {
          if(!selectedNode){
            selectedNode = _nodes[0];
            selectedNode.selected = true;
          }
          else {
            // TODO if no sliceId check only data plane successors
            nodeSiblings = SliceGraph.getNodeSuccessors(selectedNode);

            if(nodeSiblings.length === 0){
              return;
            };
            // reset current selected node
            selectedNode.selected = false;
            // find next node
            let nextNodeId = _.findIndex(_nodes, {id: nodeSiblings[0].id});
            selectedNode = _nodes[nextNodeId];
            selectedNode.selected = true;

            // NOTE I need to update sibling with successor of the parent
            // to enable vertical navigation
            let parents = SliceGraph.getNodeSuccessors(selectedNode);
            if(parents.lenght > 0){
              nodeSiblings = SliceGraph.getNodePredecessors(parents[0]);
            }
            else {
              nodeSiblings = null;
            }
          }
          drawGraph();
        };

        const selectPrevNode = () => {
          if(!selectedNode){
            selectedNode = _nodes[0];
            selectedNode.selected = true;
          }
          else {
            nodeSiblings = SliceGraph.getNodePredecessors(selectedNode);

            if(nodeSiblings.length === 0){
              return;
            };
            // reset current selected node
            selectedNode.selected = false;
            // find next node
            let prev = _.findIndex(_nodes, {id: nodeSiblings[0].id});

            if(prev < 0){
              prev = _nodes.length - 1;
            }
            selectedNode = _nodes[prev];
            selectedNode.selected = true;
          }
          drawGraph();
        };

        const sortByY = (a, b) => {
          if (a.y < b.y)
            return 1;
          if (a.y > b.y)
            return -1;
          return 0;
        };

        const getSameTypeNodes = (selectedNode) => {
          return _.filter(_nodes, n => {
            if(selectedNode.type === 'pgw' && n.type === 'button'){
              return true;
            }
            if(selectedNode.type === 'button' && n.type === 'pgw'){
              return true;
            }
            if (selectedNode.type === 'sgw' && n.type === 'mme'){
              return true;
            }
            if (selectedNode.type === 'mme' && n.type === 'sgw'){
              return true;
            }
            return n.type === selectedNode.type;
          }).sort(sortByY);
        };

        const selectNextSibling = () => {
          if(!selectedNode){
            selectedNode = _nodes[0];
            selectedNode.selected = true;
          }
          else {
            // reset current selected node
            selectedNode.selected = false;

            // find next node
            let sameTypeNodes = getSameTypeNodes(selectedNode);

            let nextSiblingId = _.findIndex(sameTypeNodes, {id: selectedNode.id}) + 1;
            if(nextSiblingId === sameTypeNodes.length){
              nextSiblingId = 0;
            }
            let nextNodeId = _.findIndex(_nodes, {id: sameTypeNodes[nextSiblingId].id});
            selectedNode = _nodes[nextNodeId];
            selectedNode.selected = true;
          }
          drawGraph();
        };

        const selectPrevSibling = () => {
          if(!selectedNode){
            selectedNode = _nodes[0];
            selectedNode.selected = true;
          }
          else {
            // reset current selected node
            selectedNode.selected = false;

            // find next node
            let sameTypeNodes = getSameTypeNodes(selectedNode);

            let nextSiblingId = _.findIndex(sameTypeNodes, {id: selectedNode.id}) - 1;
            if(nextSiblingId < 0){
              nextSiblingId = sameTypeNodes.length - 1;
            }
            let nextNodeId = _.findIndex(_nodes, {id: sameTypeNodes[nextSiblingId].id});
            selectedNode = _nodes[nextNodeId];
            selectedNode.selected = true;
          }
          drawGraph();
        };

        const drawGraph = () => {

          // svg.selectAll('.node-container').remove();
          // svg.selectAll('.link-container').remove();

          var force = d3.layout.force()
            .nodes(_nodes)
            .links(_links)
            .charge(-1060)
            .gravity(0.1)
            .linkDistance(200)
            .size([this.el.clientWidth, this.el.clientHeight])
            .on('tick', tick)
            .start();

          links = linkGroup.selectAll('.link-container')
            .data(_links, d => d.data.id)
            .enter()
            .insert('g')
            .attr({
              class: 'link-container',
              opacity: 0
            });

          links
            .transition(t)
            .attr({
              opacity: 1
            });

          links.insert('line')
            .attr('class', d => `link ${d.data.plane}`)
            .on('click', function(link ){
              selectedLink = link;

              // deselect all other links
              d3.selectAll('.link').classed('selected', false);

              d3.select(this).classed('selected', true);
            });

          nodes = nodeGroup.selectAll('.node')
            .data(_nodes, d => d.id)
            .attr({
              class: d => `node ${d.plane} ${d.type} ${d.selected ? 'selected': ''}`,
            });

          nodes
            .enter()
            .append('g')
            .attr({
              class: 'node-container',
              transform: d => d.transform,
              opacity: 0
            });

          nodes.transition(t)
            .attr({
              opacity: 1
            });

          nodes.append('rect')
            .attr({
              class: d => `node ${d.plane} ${d.type} ${d.selected ? 'selected': ''}`,
              width: 100,
              height: 50,
              x: -50,
              y: -25
            });

          nodes.append('text')
            .attr({
              'text-anchor': 'left',
              'alignment-baseline': 'middle',
              x: -20
            })
            .text(d => `${d.name}`);

          nodes.on('click', (n) => {
            expandNode(n);
          });

          // draw icons
          const ues = nodes.filter(n => n.type === 'ue');
          ues.append('path')
          .attr({
            d: mCordSlicingIcons.mobile,
            class: 'icon',
            transform: `translate(-40, -12.5), scale(0.5)`
          });

          const profiles = nodes.filter(n => n.type === 'profile');
          profiles.append('path')
          .attr({
            d: mCordSlicingIcons.profile,
            class: 'icon',
            transform: `translate(-40, -12.5), scale(0.5)`
          });

          const rru = nodes.filter(n => n.type === 'ran-ru');
          rru.append('path')
          .attr({
            d: mCordSlicingIcons.rru,
            class: 'icon',
            transform: `translate(-40, -12.5), scale(0.5)`
          });

          const rcu = nodes.filter(n => n.type === 'ran-cu');
          rcu.append('path')
          .attr({
            d: mCordSlicingIcons.rcu,
            class: 'icon',
            transform: `translate(-40, -12.5), scale(0.5)`
          });

          const sgw = nodes.filter(n => n.type === 'sgw');
          sgw.append('path')
          .attr({
            d: mCordSlicingIcons.sgw,
            class: 'icon',
            transform: `translate(-40, -12.5), scale(0.5)`
          });

          const pgw = nodes.filter(n => n.type === 'pgw');
          pgw.append('path')
          .attr({
            d: mCordSlicingIcons.pgw,
            class: 'icon',
            transform: `translate(-40, -12.5), scale(0.5)`
          });

          const mme = nodes.filter(n => n.type === 'mme');
          mme.append('path')
          .attr({
            d: mCordSlicingIcons.mme,
            class: 'icon',
            transform: `translate(-40, -12.5), scale(0.5)`
          });

          nodes
            .on('mousedown', (n) => {
              // save a reference to dragStart
              dragStartNode = n;

              dragLine
                .classed('hidden', false)
                .attr('d', 'M' + dragStartNode.x + ',' + dragStartNode.y + 'L' + dragStartNode.x + ',' + dragStartNode.y);
            })
            .on('mouseover', (n) => {
              if(dragStartNode){
                dragEndNode = n;
              }
            });

          svg
            .on('mousemove', function(){
              if(!dragStartNode){
                return;
              }
              dragLine.attr('d', 'M' + dragStartNode.x + ',' + dragStartNode.y + 'L' + d3.mouse(this)[0] + ',' + d3.mouse(this)[1]);
            })
            .on('mouseup', () => {
              if(!dragStartNode || !dragEndNode){
                resetDragInfo();
                return;
              }

              // TODO
              // [X] check that I can connect the two nodes
              // [X] check link direction
              // [ ] save the new link in the BE

              // check that I can connect the 2 nodes
              const successorType = SliceGraph.getNodeDataPlaneSuccessors(dragStartNode)[0].type;
              if(dragEndNode.type !== successorType){
                resetDragInfo();
                return;
              }

              // create the link
              _links.push({
                source: dragStartNode,
                target: dragEndNode,
                data: {
                  id: `${dragStartNode.id}.${dragEndNode.id}`,
                  source: dragStartNode.id,
                  target: dragEndNode.id
                }
              });

              // update the graph
              // TODO recalculate graph positions
              drawGraph();

              resetDragInfo();
            });

          // remove exiting nodes
          svg.selectAll('.node-container')
            .data(_nodes, d => d.id)
            .exit()
            .transition(t)
            .attr({
              opacity: 0
            })
            .remove();

          // remove exiting links
          svg.selectAll('.link-container')
            .data(_links, d => d.data.id)
            .exit()
            .transition(t)
            .attr({
              opacity: 0
            })
            .remove();
        };

        d3.select('body')
          .on('keydown', function(){
            // console.log(d3.event.code);
            if(d3.event.code === 'Backspace' && selectedLink){
              // delete link
              deleteLink(selectedLink.data.id);
            }
            if(d3.event.code === 'Enter' && selectedNode){
              d3.event.preventDefault();
              expandNode(selectedNode);
            }
            if(d3.event.code === 'Escape' && selectedNode){
              selectedNode.selected = false;
              selectedNode = null;
              nodeSiblings = null;
              drawGraph();
            }
            if(d3.event.code === 'ArrowRight'){
              d3.event.preventDefault();
              selectNextNode();
            }
            if(d3.event.code === 'ArrowLeft'){
              d3.event.preventDefault();
              selectPrevNode();
            }
            if(d3.event.code === 'ArrowUp'){
              d3.event.preventDefault();
              selectNextSibling();
            }
            if(d3.event.code === 'ArrowDown'){
              d3.event.preventDefault();
              selectPrevSibling();
            }

          });
      }
    }
  });
})();