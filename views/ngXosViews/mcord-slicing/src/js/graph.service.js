(function () {
  'use strict';

  angular.module('xos.mcord-slicing')
  .service('SliceGraph', function(_, NodePositioner){
    const g = new graphlib.Graph();

    /**
    * @ngdoc method
    * @name xos.mcord-slicing.SliceGraph#buildGraph
    * @methodOf xos.mcord-slicing.SliceGraph
    * @description
    * buildGraph
    * @param {object} data An object in the for of {nodes: [], links: []} describing the graph
    * @returns {null}
    **/
    this.buildGraph = (data) => {
      _.forEach(data.nodes, n => g.setNode(n.id, n));
      _.forEach(data.links, n => g.setEdge(n.source, n.target, n));
    };

    this.getLinks = () => {
      return g.edges().map(e => {
        return {
          source: g.node(e.v),
          target: g.node(e.w),
          data: g.edge(e)
        }
      });
    }

    this.getGraph = () => g;

    // find the successor of a node
    this.getNodeSuccessors = (node) => {
      return _.map(g.successors(node.id), n => {
        return g.node(n);
      })
    };

    this.getNodePredecessors = (node) => {
      return _.map(g.predecessors(node.id), n => {
        return g.node(n);
      });
    };

    // get data plane successors of a node
    this.getNodeDataPlaneSuccessors = (node) => {
      return _.filter(this.getNodeSuccessors(node), n => {
        return n.plane === 'data';
      });
    };

    // find the end of the graph toward upstream
    this.getUpstreamSinks = (el) => {
      const sinks =  _.reduce(g.sinks(), (sinks, node, i) => {
        let n = g.node(node);
        if(n.type === 'upstream'){
          sinks.push(n);
        }
        return sinks;
      }, []);

      return _.map(sinks, (s, i) => {
        s.position = {
          top: 0,
          bottom: el.clientHeight,
          total: sinks.length,
          index: i + 1
        };
        return s;
      })
    };

    this.positionGraph = (el) => {
      // get root node
      let nodes = this.getUpstreamSinks(el);

      // find children, recursively
      let children = [];
      _.forEach(nodes, (n, i) => {
        children = children.concat(this.findPredecessor(n));
      });
      nodes = nodes.concat(children);

      // calculate the position for all nodes
      nodes = _.map(nodes, r => {
        return NodePositioner.getDataPlaneNodePos(r, el);
      });

      return nodes;
    };

    // this iterate on all the nodes, and add position information
    this.findPredecessor = (node) => {
      let preds = g.predecessors(node.id);

      // saving predecessor information
      preds = preds.map((p, i) => {
        p = g.node(p);
        const parentAvailableSpace = (node.position.bottom - node.position.top) / node.position.total;
        const parentY = NodePositioner.getVpos(node);
        p.position = {
          top: parentY - (parentAvailableSpace / 2),
          bottom: (parentY + (parentAvailableSpace / 2)),
          total: preds.length,
          index: i + 1
        };
        return p;
      });

      //recurse
      const predsChild = _.reduce(preds, (list, p) => {
        return list.concat(this.findPredecessor(p));
      }, []);

      return preds.concat(predsChild);
    };

    this.getGraphLinks = (nodes) => {
      const links = [];
      _.forEach(nodes, n => {
        const edges = g.inEdges(n.id);
        _.forEach(edges, e => {
          links.push({
            source: g.node(e.v),
            target: g.node(e.w),
            data: g.edge(e)
          });
        });
      });
      return links;
    };

    this.getDataPlaneForSlice = (ranRu, sliceId) => {
      // hardcoded, likely to be improved
      const ranCu = g.node(g.successors(ranRu.id)[0]);
      const sgw = g.node(g.successors(ranCu.id)[0]);
      const pgw = g.node(g.successors(sgw.id)[0]);

      // augmenting nodes with sliceId
      ranRu.sliceId = sliceId;
      ranCu.sliceId = sliceId;
      sgw.sliceId = sliceId;
      pgw.sliceId = sliceId;
      return [ranRu, ranCu, sgw, pgw];
    };

    this.getControlPlaneForSlice = (dataPlane, sliceId) => {
      return _.reduce(dataPlane, (cp_nodes, dp_node) => {
        // NOTE: looks that all the time the cplane version of the node is successors number 1, we may need to check
        let cp_node = g.node(g.successors(dp_node.id)[1]);

        // position relative to their data-plane node
        cp_node = NodePositioner.getControlPlaneNodePos(cp_node, dp_node);
        cp_node.sliceId = sliceId;
        // hardcoded
        // if control plane node is a sgw, there is an MME attached
        if(cp_node.type === 'sgw'){
          let mme = g.node(g.successors(cp_node.id)[1]);
          // position relative to their data-plane node
          mme = NodePositioner.getControlPlaneNodePos(mme, cp_node);
          mme.sliceId = sliceId;
          cp_nodes.push(mme);
        }

        return cp_nodes.concat(cp_node);
      }, []);
    };

    this.activeSlices = [];
    // this.usedSlicesId = [];
    this.getSliceDetail= (node) => {
      if(node.sliceId && this.activeSlices.indexOf(node.sliceId) > -1){
        // the slice is already active, return an empty set
        return [[], []];
      }

      // let sliceId;
      // if (node.sliceId){
      //   sliceId = node.sliceId;
      // }
      // else{
        const sliceId = _.min(this.activeSlices) ? _.min(this.activeSlices) + 1 : 1;
      // }
      this.activeSlices.push(sliceId);
      // this.usedSlicesId.push(sliceId);

      // getting the beginning of the slice
      const ranRu = (function getRanRu(n) {
        if(n.type === 'ran-ru'){
          return n;
        }
        // we assume that in the slice node have only one predecessor
        const pred = g.predecessors(n.id);
        return getRanRu(g.node(pred[0]));
      })(node);

      // get data plane nodes for this slice (need them to get the corresponding control plane)
      const dp_nodes = this.getDataPlaneForSlice(ranRu, sliceId);
      // get control plane nodes for this slice
      const cp_nodes = this.getControlPlaneForSlice(dp_nodes, sliceId);

      const links = this.getGraphLinks(cp_nodes);

      // add a close button
      let closeButton = {
        name: 'Close',
        id: `close-button-${sliceId}`,
        type: 'button',
        sliceId: sliceId
      };
      closeButton = NodePositioner.getControlPlaneNodePos(closeButton, cp_nodes[3]);
      cp_nodes.push(closeButton);

      return [cp_nodes, links];
    };

    this.removeActiveSlice = sliceId => {
      // nodes are remove from the d3 nodes identified by id
      this.activeSlices.splice(this.activeSlices.indexOf(sliceId), 1);
    };

  })
  .service('NodePositioner', function(_, sliceElOrder){

    let el;

    this.storeEl = (_el) => {
      el = _el;
    };

    this.getHpos = (node, el) => {
      let elPos = sliceElOrder.indexOf(node.type) + 1;

      // hardcoded
      if(node.type === 'mme'){
        elPos = sliceElOrder.indexOf('sgw') + 1
      }
      if(node.type === 'button'){
        elPos = sliceElOrder.indexOf('pgw') + 1
      }
      let x = (el.clientWidth / (sliceElOrder.length + 1)) * elPos;
      return x;
    };

    this.getVpos = (node) => {
      // calculate the available space to distribute items
      const availableSpace = node.position.bottom - node.position.top;

      // calculate the distance between each item
      const step = availableSpace / (node.position.total + 1);

      // vertical position
      const y = (step * node.position.index) + node.position.top;
      return y;
    };

    // for nodes that are part of the data plane
    this.getDataPlaneNodePos = (node) => {
      const x = this.getHpos(node, el);
      const y = this.getVpos(node);
      node.x = x;
      node.y = y;
      node.transform = `translate(${x}, ${y})`;
      node.fixed = true;
      return node;
    };

    // control element nodes are positioned relatively to their corresponding data plane node
    this.getControlPlaneNodePos = (cp_node, dp_node) => {
      const x = this.getHpos(cp_node, el);
      const y = dp_node.y - 75;
      cp_node.x = x;
      cp_node.y = y;
      cp_node.transform = `translate(${x}, ${y})`;
      cp_node.fixed = true;
      return cp_node;
    };

  })
  .value('sliceElOrder', [
    'ue',
    'profile',
    'ran-ru',
    'ran-cu',
    'sgw',
    'pgw',
    'upstream'
  ]);
})();
