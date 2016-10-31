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
  ])
  .constant('mCordSlicingIcons', {
    mobile: `M26.1,0c0.5,0.2,1.1,0.4,1.6,0.7C28.7,1.4,29,2.4,29,3.5c0,0.2,0,0.4,0,0.6c0,14,0,28.1,0,42.1c0,1-0.2,1.8-0.9,2.6
  c-0.4,0.5-0.9,0.8-1.5,1c-0.2,0.1-0.3,0.1-0.5,0.2c-7.7,0-15.5,0-23.2,0c-0.5-0.2-1.1-0.4-1.5-0.7c-1-0.7-1.4-1.7-1.4-2.9
  c0-3.8,0-7.6,0-11.4C0,24.5,0,14.1,0,3.8c0-1,0.2-1.8,0.9-2.6c0.4-0.5,0.9-0.8,1.5-1C2.6,0.1,2.7,0.1,2.9,0C10.6,0,18.4,0,26.1,0z
   M26.7,43.7c0-12.8,0-25.6,0-38.3c-8.1,0-16.2,0-24.3,0c0,12.8,0,25.6,0,38.3C10.5,43.7,18.6,43.7,26.7,43.7z M16.2,46.6
  c0-0.9-0.8-1.7-1.7-1.7c-0.9,0-1.7,0.8-1.7,1.7c0,0.9,0.8,1.7,1.7,1.7C15.5,48.3,16.2,47.5,16.2,46.6z M14.5,3.3c0.8,0,1.5,0,2.3,0
  c0.4,0,0.8,0,1.2,0c0.3,0,0.4-0.1,0.5-0.4c0-0.3-0.2-0.4-0.4-0.4c-0.1,0-0.2,0-0.2,0c-2.2,0-4.4,0-6.6,0c-0.1,0-0.3,0-0.4,0.1
  c-0.1,0.1-0.3,0.3-0.3,0.4c0,0.1,0.2,0.3,0.3,0.4c0.1,0.1,0.2,0,0.4,0C12.3,3.3,13.4,3.3,14.5,3.3z`,
    profile: `M29,24.4c-0.6,0.2-1.2,0.3-1.8,0.5c-0.2,0-0.2,0.1-0.2,0.3c0,0.9,0.1,1.8,0,2.7c-0.1,0.8-0.7,1.4-1.6,1.4
    c-0.8,0-1.4-0.7-1.5-1.5c0-0.4,0.1-0.9,0.1-1.3c0-4.5-3.3-8.5-7.8-9.3c-5.1-0.9-9.9,2.2-11.1,7.1C3.8,29.7,7.3,35,12.7,36
    c0.9,0.2,1.8,0.2,2.7,0.1c0.8-0.1,1.5,0.3,1.7,1.1c0.2,0.8-0.1,1.5-0.9,1.8c-0.3,0.1-0.7,0.2-1,0.2c-0.8,0-1.5,0-2.4,0
    c-0.2,0.6-0.3,1.3-0.5,1.9c0,0,0,0-0.1,0c-0.1,0-0.2-0.1-0.3-0.1c-0.9-0.3-1.9-0.5-2.8-0.8c0.2-0.6,0.3-1.2,0.5-1.8
    c0.1-0.2,0-0.3-0.2-0.3c-0.4-0.2-0.8-0.4-1.2-0.6c-0.5-0.3-0.9-0.6-1.4-0.9c-0.5,0.5-0.9,1-1.4,1.4c-0.8-0.8-1.6-1.6-2.4-2.4
    c0.5-0.5,1-0.9,1.4-1.4c-0.5-0.9-1-1.8-1.5-2.7c-0.1-0.1-0.2-0.1-0.3-0.1c-0.6,0.2-1.2,0.3-1.8,0.5c-0.1-0.5-0.2-0.9-0.4-1.4
    C0.2,30,0,29.4-0.2,28.8c0,0,0,0,0-0.1c0.6-0.2,1.2-0.3,1.8-0.5c0.2,0,0.2-0.1,0.2-0.3c0-0.9,0-1.9,0-2.8c0-0.2,0-0.2-0.2-0.3
    c-0.6-0.2-1.2-0.3-1.8-0.5c0,0,0,0,0-0.1c0-0.1,0.1-0.2,0.1-0.3c0.3-0.9,0.5-1.9,0.8-2.8c0.6,0.2,1.2,0.3,1.8,0.5
    c0.2,0.1,0.3,0,0.3-0.2c0.5-0.8,1-1.6,1.4-2.5c0,0,0.1-0.1,0.1-0.2c-0.5-0.5-1-0.9-1.4-1.4c0.8-0.8,1.6-1.6,2.4-2.4
    c0.5,0.5,0.9,1,1.3,1.4c0.9-0.5,1.8-1,2.7-1.5c0.1,0,0.1-0.2,0.1-0.3c-0.1-0.6-0.3-1.2-0.5-1.8c0.4-0.1,0.8-0.2,1.1-0.3
    c0.7-0.2,1.4-0.4,2-0.6c0,0,0,0,0.1,0c0.2,0.6,0.3,1.2,0.5,1.8c0,0.2,0.1,0.2,0.3,0.2c0.9,0,1.9,0,2.8,0c0.2,0,0.2,0,0.3-0.2
    c0.2-0.6,0.3-1.2,0.5-1.8c0,0,0,0,0.1,0c0.1,0,0.2,0.1,0.3,0.1c0.9,0.3,1.9,0.5,2.8,0.8c-0.2,0.6-0.3,1.2-0.5,1.8
    c-0.1,0.2,0,0.3,0.2,0.3c0.6,0.3,1.2,0.6,1.7,0.9c0.3,0.2,0.6,0.4,0.9,0.6c0.5-0.5,1-1,1.4-1.4c0.8,0.8,1.6,1.6,2.4,2.4
    c-0.5,0.5-1,0.9-1.4,1.4c0.5,0.9,1,1.8,1.5,2.7c0.1,0.1,0.2,0.1,0.3,0.1c0.6-0.2,1.2-0.3,1.8-0.5c0.1,0.4,0.2,0.8,0.3,1.1
    C28.7,23,28.9,23.7,29,24.4C29,24.4,29,24.4,29,24.4z
    M13.6,20.4c1.2-0.1,2.3-0.4,3.4,0c0.7,0.3,1.3,0.7,1.8,1.4c0.5,0.7,1.1,1.4,1.6,2.2c0.8,1.1,0.9,2.4,0.3,3.7
    c-0.1,0.3-0.4,0.6-0.3,0.8c0,0.2,0.4,0.4,0.6,0.6c1.7,1.7,3.3,3.3,5,5c1.5,1.6,0.8,4.2-1.4,4.7c-1,0.2-1.9-0.1-2.7-0.8
    c-1.6-1.6-3.1-3.1-4.7-4.7c-0.2-0.2-0.5-0.5-0.7-0.7c-0.1-0.2-0.3-0.2-0.5-0.1c-0.8,0.1-1.5,0.3-2.3,0.4c-1.3,0.1-2.4-0.3-3.2-1.3
    c-0.6-0.8-1.3-1.6-1.8-2.5c-0.7-1-0.8-2.1-0.5-3.2c0.2-0.6,0.5-1.3,0.8-1.9C9,24,9.1,24,9.2,24.1c1,1.4,2.1,2.8,3.1,4.2
    c0.4,0.5,0.6,0.6,1.2,0.4c0.5-0.2,1.1-0.3,1.6-0.5c0.4-0.1,0.7-0.3,0.9-0.7c0.3-0.5,0.7-1,1-1.5c0.3-0.4,0.3-0.7,0-1.1
    c-1.1-1.4-2.1-2.9-3.2-4.3C13.7,20.6,13.7,20.6,13.6,20.4z`,
    rru: `M18.4,44.2c-2.6,0-5.1,0-7.8,0c0.6-4.7,1.2-9.4,1.9-14c0.4-2.7,0.9-5.5,1.3-8.2c0.1-0.5-0.2-1.1-0.5-1.4
    c-0.8-0.9-1-2-0.1-2.7c0.6-0.4,1.9-0.5,2.5-0.1c1,0.6,0.8,1.7,0.2,2.7c-0.4,0.6-0.6,1.5-0.5,2.2c1,7,2,13.9,3,20.9
    C18.4,43.7,18.4,43.9,18.4,44.2z
    M9.4,7.3c-8.5,4.5-9.5,13.8-5,19.6c1,1.2,2.3,2.3,3.6,3.2c0.9,0.6,1.3,1.2,0.5,2.1c-4.7-1.7-8.4-7-8.6-12.5
    c-0.2-6,3.2-11.5,8.8-13.8C9,6.3,9.2,6.8,9.4,7.3z
    M20.3,5.9c5,1.8,8.7,7.2,8.7,12.9c0,6-3.4,11.4-8.5,13.3c-0.5-0.9-0.4-1.5,0.6-2.1c8.5-5.5,8.3-16.8-0.3-22.1
    c-0.5-0.3-0.8-1.1-1.1-1.6C19.9,6.2,20.1,6.1,20.3,5.9z
    M9.4,28.9c-3.6-2-5.7-5-5.8-9.2C3.3,15,5.5,11.5,9.6,9.2c0.7,0.9,0.7,1.5-0.3,2.2c-5.5,4.2-5.5,11-0.2,15.4
    c0.5,0.4,0.6,1.2,0.9,1.8C9.8,28.7,9.6,28.8,9.4,28.9z
    M19.3,28.5c0.2-0.6,0.3-1.4,0.8-1.8c5.4-4.7,5.2-11.4-0.6-15.6c-0.1-0.1-0.3-0.2-0.5-0.4c0.1-0.5,0.3-1,0.4-1.6
    c4,2.2,6.2,5.4,6.2,9.8c0.1,4.4-2,7.6-5.7,9.9C19.7,28.7,19.5,28.6,19.3,28.5z
    M10.2,25.3c-4.6-3.3-4.4-10,0.9-12.4c-0.3,0.7-0.4,1.5-0.9,2.1c-2.1,2.5-2.1,5.4,0,8.1c0.4,0.5,0.4,1.3,0.6,2
    C10.6,25.2,10.4,25.3,10.2,25.3z
    M18.4,25c0.2-0.7,0.3-1.6,0.8-2.2c1.8-2.6,1.7-5.4-0.4-7.8c-0.8-1-0.8-1-0.2-2.3c4.6,2.9,4.8,9.1,0.4,12.4
    C18.8,25.2,18.6,25.1,18.4,25z`,
    rcu: `M0,35.7c0.1-0.4,0.3-0.8,0.7-0.9c0.2-0.1,0.5-0.2,0.8-0.2c2.9,0,5.8,0,8.7,0c0.1,0,0.2,0,0.4,0c0.2,0,0.2-0.1,0.2-0.2
    c0-0.2,0-0.4,0-0.6c0.1-0.4,0.4-0.7,0.8-0.8c0.1,0,0.2,0,0.3,0c1.7,0,3.4,0,5.1,0c0.8,0,1.2,0.4,1.2,1.2c0,0.5,0,0.4,0.4,0.4
    c2.9,0,5.8,0,8.7,0c0.9,0,1.5,0.2,1.8,1.1c0,0.2,0,0.3,0,0.5c-0.3,0.8-0.9,1.1-1.7,1.1c-2.9,0-5.8,0-8.6,0c-0.4,0-0.4,0-0.4,0.4
    c0,0.1,0,0.1,0,0.2c0,0.6-0.4,1-1,1c-1.8,0-3.6,0-5.4,0c-0.4,0-0.7-0.1-0.8-0.5c-0.1-0.2-0.1-0.5-0.2-0.8c0-0.3,0-0.3-0.3-0.3
    c-3,0-6,0-9,0c-0.4,0-0.7-0.1-1-0.3c-0.3-0.2-0.4-0.5-0.5-0.8C0,36,0,35.9,0,35.7z M14.5,35c-0.5,0-1,0-1.5,0c-0.1,0-0.2,0-0.2,0.2
    c0,0.5,0,1,0,1.5c0,0.2,0,0.2,0.2,0.2c1,0,2,0,3,0c0.1,0,0.2,0,0.2-0.2c0-0.5,0-1,0-1.4c0-0.2-0.1-0.2-0.2-0.2
    C15.5,35,15,35,14.5,35z
    M14.5,31.4c-4,0-8.1,0-12.1,0c-0.5,0-0.9-0.1-1.2-0.5C1,30.7,1,30.4,0.9,30.2c0-0.1,0-0.2,0-0.3c0-5.7,0-11.5,0-17.2
    c0-0.3,0.1-0.6,0.2-0.9c0.2-0.4,0.6-0.6,1-0.6c0.1,0,0.2,0,0.3,0c8.1,0,16.2,0,24.3,0c0.5,0,0.9,0.1,1.2,0.5
    c0.1,0.2,0.2,0.4,0.3,0.7c0,0.1,0,0.2,0,0.3c0,5.8,0,11.6,0,17.3c0,0.3-0.1,0.7-0.3,1c-0.3,0.4-0.7,0.5-1.2,0.5c-2.7,0-5.4,0-8.2,0
    C17.2,31.4,15.9,31.4,14.5,31.4z M4.4,20.6c6.8,0,13.5,0,20.3,0c0-0.1,0-0.2,0-0.2c0-1.6,0-3.3,0-4.9c0-0.2-0.1-0.3-0.3-0.3
    c-6.6,0-13.1,0-19.7,0c-0.2,0-0.3,0.1-0.3,0.3c0,1.6,0,3.2,0,4.9C4.4,20.5,4.4,20.5,4.4,20.6z M4.4,27.3c6.8,0,13.5,0,20.2,0
    c0-1.8,0-3.6,0-5.4c-6.8,0-13.5,0-20.2,0C4.4,23.7,4.4,25.5,4.4,27.3z
    M23.3,16.6c0,0.1,0,0.2,0,0.2c0,0.7,0,1.5,0,2.2c0,0.2-0.1,0.3-0.3,0.3c-3.3,0-6.7,0-10,0c-2.3,0-4.7,0-7,0
    c-0.2,0-0.3,0-0.3-0.3c0-0.7,0-1.5,0-2.2c0-0.1,0-0.2,0-0.2C11.6,16.6,17.4,16.6,23.3,16.6z M7.7,18.6c0-0.4,0-0.8,0-1.2
    c0,0-0.1-0.1-0.1-0.1c-0.4,0-0.8,0-1.2,0c0,0.5,0,0.9,0,1.3C6.9,18.6,7.3,18.6,7.7,18.6z M8.4,17.3c0,0.5,0,0.9,0,1.3
    c0.4,0,0.9,0,1.3,0c0-0.4,0-0.8,0-1.2c0,0-0.1-0.1-0.1-0.1C9.2,17.3,8.8,17.3,8.4,17.3z M10.4,18.6c0.5,0,0.9,0,1.3,0
    c0-0.4,0-0.9,0-1.3c-0.4,0-0.8,0-1.2,0c0,0-0.1,0.1-0.1,0.1C10.4,17.8,10.4,18.2,10.4,18.6z
    M14.5,23.2c2.8,0,5.7,0,8.5,0c0.3,0,0.3,0,0.3,0.3c0,0.7,0,1.4,0,2.1c0,0.2-0.1,0.3-0.3,0.3c-4.6,0-9.2,0-13.7,0
    c-1.1,0-2.2,0-3.3,0c-0.2,0-0.3-0.1-0.3-0.3c0-0.7,0-1.5,0-2.2c0-0.2,0.1-0.3,0.3-0.3C8.8,23.2,11.7,23.2,14.5,23.2z M6.4,25.2
    c0.4,0,0.8,0,1.2,0c0.1,0,0.1-0.1,0.1-0.1c0-0.3,0-0.7,0-1c0,0-0.1-0.1-0.1-0.1c-0.4,0-0.8,0-1.2,0C6.4,24.4,6.4,24.8,6.4,25.2z
     M8.4,25.2c0.4,0,0.8,0,1.2,0c0,0,0.1-0.1,0.1-0.2c0-0.2,0-0.5,0-0.7c0-0.5,0.1-0.4-0.4-0.4c-0.3,0-0.6,0-0.9,0
    C8.4,24.4,8.4,24.8,8.4,25.2z M11.7,23.9c-0.4,0-0.8,0-1.2,0c0,0-0.1,0.1-0.1,0.1c0,0.4,0,0.8,0,1.2c0.5,0,0.9,0,1.3,0
    C11.7,24.8,11.7,24.4,11.7,23.9z`,
    sgw: `M24.2,11.6c0.5,0.2,0.7,0.6,0.9,1.1c1.3,4.8,2.6,9.5,3.9,14.3c0,0.2,0.1,0.3,0.1,0.5c0,1.8,0,3.6,0,5.4
    c0,0.9-0.4,1.4-1.4,1.4c-4.1,0-8.1,0-12.2,0c-0.1,0-0.2,0-0.4,0c0,1,0,1.9,0,2.9c0.1,0,0.2,0,0.4,0c3.1,0,6.1,0,9.2,0
    c0.1,0,0.2,0,0.4,0c0.3,0,0.5,0.3,0.5,0.5c0,0.3-0.2,0.5-0.5,0.6c-0.1,0-0.2,0-0.3,0c-6.8,0-13.7,0-20.5,0c-0.5,0-0.8-0.2-0.8-0.6
    c0-0.4,0.3-0.6,0.8-0.6c3.1,0,6.2,0,9.3,0c0.1,0,0.2,0,0.4,0c0-1,0-1.9,0-2.9c-0.1,0-0.2,0-0.4,0c-4,0-8.1,0-12.1,0
    c-0.7,0-1.2-0.2-1.5-0.9c0-2.1,0-4.2,0-6.2c0.1-0.2,0.1-0.3,0.2-0.5C1.4,22,2.7,17.4,4,12.7c0.1-0.5,0.4-0.9,0.9-1.1
    C11.3,11.6,17.7,11.6,24.2,11.6z M23.9,12.8c-6.2,0-12.5,0-18.7,0C4,17.3,2.7,21.7,1.5,26.1c8.7,0,17.3,0,26,0
    C26.3,21.7,25.1,17.2,23.9,12.8z M1.2,27.3c0,2,0,3.9,0,5.8c8.9,0,17.8,0,26.7,0c0-1.9,0-3.9,0-5.8C19,27.3,10.1,27.3,1.2,27.3z
    M12.7,21.1c0.1,0.4,0.2,0.7,0.3,0.8c0.3,0.3,0.8,0.5,1.5,0.5c0.4,0,0.8,0,1-0.1c0.5-0.2,0.7-0.5,0.7-1
      c0-0.3-0.1-0.5-0.4-0.6c-0.2-0.1-0.6-0.3-1.1-0.4l-0.9-0.2c-0.9-0.2-1.5-0.4-1.8-0.6c-0.6-0.4-0.8-1-0.8-1.8
      c0-0.7,0.3-1.4,0.8-1.8c0.5-0.5,1.3-0.7,2.4-0.7c0.9,0,1.6,0.2,2.3,0.7c0.6,0.5,0.9,1.1,1,2H16c0-0.5-0.3-0.8-0.7-1.1
      c-0.3-0.1-0.6-0.2-1-0.2c-0.5,0-0.8,0.1-1.1,0.3c-0.3,0.2-0.4,0.4-0.4,0.8c0,0.3,0.1,0.5,0.4,0.7c0.2,0.1,0.5,0.2,1.1,0.3l1.4,0.3
      c0.6,0.1,1.1,0.3,1.4,0.6c0.5,0.4,0.7,1,0.7,1.7c0,0.8-0.3,1.4-0.9,1.9c-0.6,0.5-1.4,0.7-2.5,0.7c-1.1,0-1.9-0.2-2.6-0.7
      c-0.6-0.5-0.9-1.2-0.9-2H12.7z`,
    pgw: `M24.2,11.6c0.5,0.2,0.7,0.6,0.9,1.1c1.3,4.8,2.6,9.5,3.9,14.3c0,0.2,0.1,0.3,0.1,0.5c0,1.8,0,3.6,0,5.4
    c0,0.9-0.4,1.4-1.4,1.4c-4.1,0-8.1,0-12.2,0c-0.1,0-0.2,0-0.4,0c0,1,0,1.9,0,2.9c0.1,0,0.2,0,0.4,0c3.1,0,6.1,0,9.2,0
    c0.1,0,0.2,0,0.4,0c0.3,0,0.5,0.3,0.5,0.5c0,0.3-0.2,0.5-0.5,0.6c-0.1,0-0.2,0-0.3,0c-6.8,0-13.7,0-20.5,0c-0.5,0-0.8-0.2-0.8-0.6
    c0-0.4,0.3-0.6,0.8-0.6c3.1,0,6.2,0,9.3,0c0.1,0,0.2,0,0.4,0c0-1,0-1.9,0-2.9c-0.1,0-0.2,0-0.4,0c-4,0-8.1,0-12.1,0
    c-0.7,0-1.2-0.2-1.5-0.9c0-2.1,0-4.2,0-6.2c0.1-0.2,0.1-0.3,0.2-0.5C1.4,22,2.7,17.4,4,12.7c0.1-0.5,0.4-0.9,0.9-1.1
    C11.3,11.6,17.7,11.6,24.2,11.6z M23.9,12.8c-6.2,0-12.5,0-18.7,0C4,17.3,2.7,21.7,1.5,26.1c8.7,0,17.3,0,26,0
    C26.3,21.7,25.1,17.2,23.9,12.8z M1.2,27.3c0,2,0,3.9,0,5.8c8.9,0,17.8,0,26.7,0c0-1.9,0-3.9,0-5.8C19,27.3,10.1,27.3,1.2,27.3zM17,20.1c-0.5,0.4-1.2,0.6-2.2,0.6H13v3.1h-1.8v-8.7H15c0.9,0,1.5,0.2,2.1,0.7c0.5,0.4,0.8,1.1,0.8,2.1
      C17.8,18.9,17.6,19.6,17,20.1z M15.7,16.9c-0.2-0.2-0.6-0.3-1-0.3H13v2.6h1.6c0.4,0,0.7-0.1,1-0.3c0.2-0.2,0.3-0.5,0.3-1
      C16,17.4,15.9,17.1,15.7,16.9z`,
    mme: `M7.9,37.9C8.5,37,9,36.1,9.5,35.2c0.6,0.2,1.2,0.5,1.8,0.6c6.4,1.9,13-2,14.4-8.6c1.3-6.2-2.9-12.4-9.2-13.4
    c-3.7-0.6-6.9,0.4-9.7,2.8c-0.1,0.1-0.1,0.1-0.2,0.2c0,0,0,0.1-0.1,0.1c0.8,0.8,1.6,1.6,2.5,2.5C5.9,20,3,20.5,0,21.1
    c0.5-3,1.1-5.9,1.6-8.9c0.8,0.8,1.6,1.7,2.5,2.5c1.2-1.1,2.4-2,3.8-2.6c5.3-2.4,10.5-2.2,15.3,1.3c3.5,2.5,5.4,6,5.8,10.4
    c0.6,6.8-3.6,13.1-10.2,15.1C15.2,40,11.6,39.7,8.2,38C8.1,38,8,37.9,7.9,37.9z
    M21.8,27.9c-3.1,0-6.1,0-9.2,0c0-3.3,0-6.6,0-10c0.9,0,1.9,0,2.8,0c0,2.4,0,4.7,0,7.1c2.1,0,4.2,0,6.4,0
    C21.8,26,21.8,26.9,21.8,27.9z
    M3.5,34.4c0.9-0.6,1.7-1.2,2.6-1.8c0.5,0.5,1.1,1,1.6,1.5c-0.5,0.9-1,1.8-1.6,2.7C5.1,36.1,4.3,35.3,3.5,34.4z
    M0.8,29.7c1.1-0.3,2.1-0.5,3.1-0.8c0.3,0.7,0.6,1.3,1,2c-0.8,0.6-1.7,1.2-2.6,1.9C1.7,31.7,1.2,30.7,0.8,29.7z
    M3.2,24.7c0.1,0.7,0.1,1.4,0.2,2.1c-1,0.3-2,0.5-3.1,0.8c-0.1-1-0.2-1.9-0.2-2.9C1.1,24.7,2.2,24.7,3.2,24.7z`
  });
})();
