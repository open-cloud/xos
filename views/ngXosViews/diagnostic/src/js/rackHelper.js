(function () {
  angular.module('xos.diagnostic')
  .service('RackHelper', function(serviceTopologyConfig, _){

    this.getComputeNodeLabelSize = () => {
      return serviceTopologyConfig.computeNode.labelHeight + (serviceTopologyConfig.instance.margin * 2)
    }

    /**
    * Given a list of instance should get the Compute Node size.
    * They are placed in rows of 2 with 5px margin on each side.
    */
   
    this.getComputeNodeSize = _.memoize((instances) => {
      const width = (serviceTopologyConfig.instance.margin * 3) + (serviceTopologyConfig.instance.width *2);

      const rows = Math.round(instances.length / 2);

      const labelSpace = this.getComputeNodeLabelSize();

      const height = (serviceTopologyConfig.instance.height * rows) + (serviceTopologyConfig.instance.margin * (rows + 1)) + labelSpace;

      return [width, height];
    });

    /**
    * Give a list on Compute Node should calculate the Rack Size.
    * Compute nodes are placed in a single column with 5px margin on each side.
    */
    this.getRackSize = (nodes) => {

      let width = 0;
      let height = serviceTopologyConfig.computeNode.margin;

      _.forEach(nodes, (node) => {
        let [nodeWidth, nodeHeight] = this.getComputeNodeSize(node.instances);

        width = nodeWidth + (serviceTopologyConfig.computeNode.margin * 2);
        height += (nodeHeight + serviceTopologyConfig.computeNode.margin);
      });

      return [width, height];
    };

    /**
    * Given an instance index, return the coordinates
    */
   
    this.getInstancePosition = (position) => {
      const row = Math.floor(position / 2);
      const column = (position % 2) ? 1 : 0;

      // add ComputeNode label size
      const labelSpace = this.getComputeNodeLabelSize();

      // x = margin + (width * column) + ( maring * column)
      const x = serviceTopologyConfig.instance.margin + (serviceTopologyConfig.instance.width * column) + (serviceTopologyConfig.instance.margin * column);

      // y = label + margin + (height * row) + ( maring * row)
      const y = labelSpace + serviceTopologyConfig.instance.margin + (serviceTopologyConfig.instance.height * row) + (serviceTopologyConfig.instance.margin * row);
      return [x, y];
    };

    /**
    * Given an Compute Node index, return the coordinates
    */

    this.getComputeNodePosition = (nodes, position) => {

      const x = serviceTopologyConfig.computeNode.margin;

      let previousElEight = _.reduce(nodes.slice(0, position), (val, node) => {
        return val + this.getComputeNodeSize(node.instances)[1]
      }, 0);

      const y =
        serviceTopologyConfig.computeNode.margin
        + (serviceTopologyConfig.computeNode.margin * position)
        + previousElEight;

      return [x, y];
    };

  });
})();
