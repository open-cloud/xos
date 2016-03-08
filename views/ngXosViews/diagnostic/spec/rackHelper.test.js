(function () {
  'use strict';

  const computeNodes = [
    {
      humanReadableName: 'cp-1.teone.xos-pg0.clemson.cloudlab.us',
      instances: [
        {
          instance_name: 'mysite_clients-3'
        },
        {
          instance_name: 'mysite_clients-4'
        },
        {
          instance_name: 'mysite_clients-5'
        }
      ]
    },
    {
      humanReadableName: 'cp-2.teone.xos-pg0.clemson.cloudlab.us',
      instances: [
        {
          instance_name: 'mysite_clients-1'
        },
        {
          instance_name: 'mysite_clients-2'
        }
      ]
    },
    {
      humanReadableName: 'cp-2.teone.xos-pg0.clemson.cloudlab.us',
      instances: [
        {
          instance_name: 'mysite_clients-1'
        },
        {
          instance_name: 'mysite_clients-2'
        }
      ]
    }
  ];

  describe('The Rack Helper Service', () => {
    
    var Service, Config;

    // results
    var cp1, cp2, cp3, rack, instancePos, nodePos;

    beforeEach(module('xos.diagnostic'));

    // inject the rackHelper service
    beforeEach(inject(function (_RackHelper_, _serviceTopologyConfig_) {
      // The injector unwraps the underscores (_) from around the parameter names when matching
      Service = _RackHelper_;
      Config = _serviceTopologyConfig_;

      cp1 = {
        width: (Config.instance.width * 2) + (Config.instance.margin * 3),
        height: (Config.instance.height * 2) + (Config.instance.margin * 5) + Config.computeNode.labelHeight
      };

      cp2 = {
        width: (Config.instance.width * 2) + (Config.instance.margin * 3),
        height: Config.instance.height + (Config.instance.margin * 4) + Config.computeNode.labelHeight
      };

      cp3 = {
        width: (Config.instance.width * 2) + (Config.instance.margin * 3),
        height: Config.instance.height + (Config.instance.margin * 4) + Config.computeNode.labelHeight
      };

      rack = {
        width: cp1.width + (Config.computeNode.margin * 2),
        height: cp1.height + cp2.height + cp3.height + (Config.computeNode.margin * 4)
      }

      instancePos = [
        {
          x: Config.instance.margin,
          y: Config.instance.margin + Service.getComputeNodeLabelSize()
        },
        {
          x: Config.instance.margin + (Config.instance.width * 1) + (Config.instance.margin * 1),
          y: Config.instance.margin + Service.getComputeNodeLabelSize()
        },
        {
          x: Config.instance.margin,
          y: Config.instance.margin + Service.getComputeNodeLabelSize() + + (Config.instance.height * 1) + (Config.instance.margin * 1)
        },
        {
          x: Config.instance.margin + (Config.instance.width * 1) + (Config.instance.margin * 1),
          y: Config.instance.margin + Service.getComputeNodeLabelSize() + + (Config.instance.height * 1) + (Config.instance.margin * 1)
        }
      ];

      nodePos = [
        {
          x: Config.computeNode.margin,
          y: Config.computeNode.margin
        },
        {
          x: Config.computeNode.margin,
          y: (Config.computeNode.margin * 2) + cp1.height
        },
        {
          x: Config.computeNode.margin,
          y: (Config.computeNode.margin * 3) + cp1.height + cp2.height
        }
      ]
    }));

    describe('Given a list of instances', () => {
      it('should calculate the first Compute Node Size', () => {
        const [width, height] = Service.getComputeNodeSize(computeNodes[0].instances);
        expect(width).toBe(cp1.width);
        expect(height).toBe(cp1.height);
      });

      it('should calculate the second Compute Node Size', () => {
        const [width, height] = Service.getComputeNodeSize(computeNodes[1].instances);
        expect(width).toBe(cp2.width);
        expect(height).toBe(cp2.height);
      });

      it('should calculate the third Compute Node Size', () => {
        const [width, height] = Service.getComputeNodeSize(computeNodes[1].instances);
        expect(width).toBe(cp3.width);
        expect(height).toBe(cp3.height);
      });
    });

    describe('Given a list of Compute Nodes', () => {
      it('should return rack size', () => {
        const [width, height] = Service.getRackSize(computeNodes);
        expect(width).toBe(rack.width);
        expect(height).toBe(rack.height);
      });
    });

    describe('Given an instance index', () => {
      it('should return the position for first instance', () => {
        const [x, y] = Service.getInstancePosition(0);
        expect(x).toBe(instancePos[0].x);
        expect(y).toBe(instancePos[0].y);
      })

      it('should return the position for second instance', () => {
        const [x, y] = Service.getInstancePosition(1);
        expect(x).toBe(instancePos[1].x);
        expect(y).toBe(instancePos[1].y);
      });

      it('should return the position for third instance', () => {
        const [x, y] = Service.getInstancePosition(2);
        expect(x).toBe(instancePos[2].x);
        expect(y).toBe(instancePos[2].y);
      });

      it('should return the position for 4th instance', () => {
        const [x, y] = Service.getInstancePosition(3);
        expect(x).toBe(instancePos[3].x);
        expect(y).toBe(instancePos[3].y);
      });
    });

    describe('Given an ComputeNode index', () => {
      it('should return the position for 1st node', () => {
        const [x, y] = Service.getComputeNodePosition(computeNodes, 0);
        expect(x).toBe(nodePos[0].x);
        expect(y).toBe(nodePos[0].y);
      })

      it('should return the position for 2st node', () => {
        const [x, y] = Service.getComputeNodePosition(computeNodes, 1);
        expect(x).toBe(nodePos[1].x);
        expect(y).toBe(nodePos[1].y);
      });

      it('should return the position for 2st node', () => {
        const [x, y] = Service.getComputeNodePosition(computeNodes, 2);
        expect(x).toBe(nodePos[2].x);
        expect(y).toBe(nodePos[2].y);
      });
    });
  });
})();
