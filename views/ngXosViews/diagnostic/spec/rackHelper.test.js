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
    
    var Service;

    beforeEach(module('xos.serviceTopology'));

    // inject the rackHelper service
    beforeEach(inject(function (_RackHelper_) {
      // The injector unwraps the underscores (_) from around the parameter names when matching
      Service = _RackHelper_;
    }));

    describe('Given a list of instances', () => {
      it('should calculate the Compute Node Size', () => {
        const [width, height] = Service.getComputeNodeSize(computeNodes[0].instances);
        expect(width).toBe(95);
        expect(height).toBe(67);
      });
    });

    describe('Given a list of Compute Nodes', () => {
      it('should return rack size', () => {
        const [width, height] = Service.getRackSize(computeNodes);
        expect(width).toBe(105);
        expect(height).toBe(179);
      });
    });

    describe('Given an instance index', () => {
      it('should return the position for first instance', () => {
        const [x, y] = Service.getInstancePosition(0);
        expect(x).toBe(5);
        expect(y).toBe(25);
      });

      it('should return the position for second instance', () => {
        const [x, y] = Service.getInstancePosition(1);
        expect(x).toBe(50);
        expect(y).toBe(25);
      });

      it('should return the position for third instance', () => {
        const [x, y] = Service.getInstancePosition(2);
        expect(x).toBe(5);
        expect(y).toBe(46);
      });

      it('should return the position for 4th instance', () => {
        const [x, y] = Service.getInstancePosition(3);
        expect(x).toBe(50);
        expect(y).toBe(46);
      });
    });

    describe('Given an ComputeNode index', () => {
      it('should return the position for 1st node', () => {
        const [x, y] = Service.getComputeNodePosition(computeNodes, 0);
        expect(x).toBe(5);
        expect(y).toBe(5);
      });

      it('should return the position for 2st node', () => {
        const [x, y] = Service.getComputeNodePosition(computeNodes, 1);
        expect(x).toBe(5);
        expect(y).toBe(77);
      });

      it('should return the position for 2st node', () => {
        const [x, y] = Service.getComputeNodePosition(computeNodes, 2);
        expect(x).toBe(5);
        expect(y).toBe(128);
      });
    });
  });
})();
