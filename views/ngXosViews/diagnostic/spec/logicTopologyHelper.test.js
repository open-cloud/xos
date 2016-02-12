(function () {
  'use strict';

  describe('The Logic Topology Helper Service', () => {
    
    var Service;

    beforeEach(module('xos.serviceTopology'));

    // inject the rackHelper service
    beforeEach(inject(function (_LogicTopologyHelper_) {
      // The injector unwraps the underscores (_) from around the parameter names when matching
      Service = _LogicTopologyHelper_;
    }));

    var customMatchers = {
      toBeSimilar: () => {

        const tolerance = 0.1;

        return {
          compare: (actual, expected) => {
            return {
              pass: (Math.abs(actual - expected) < tolerance),
              message: `Expected ${actual} to be ${expected}`
            }
          }
        }
      }
    };

    beforeEach(function() {
      jasmine.addMatchers(customMatchers);
    });

    it('should calculate horizontal position for each element', () => {
      let [el0x, el1x, el2x, el3x, el4x, el5x] = Service.computeElementPosition(900);

      expect(el0x).toBeSimilar(870);
      expect(el1x).toBeSimilar(736.6);
      expect(el2x).toBeSimilar(560.7);
      expect(el3x).toBeSimilar(384.8);
      expect(el4x).toBeSimilar(251.4);
      expect(el5x).toBeSimilar(95);
    });
  });

})();
