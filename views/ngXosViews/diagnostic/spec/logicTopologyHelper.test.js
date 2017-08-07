
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


(function () {
  'use strict';

  describe('The Logic Topology Helper Service', () => {
    
    var Service, Config;

    var x0, x1, x2, x3, x4;

    var svgWidth = 900;

    beforeEach(module('xos.diagnostic'));

    // inject the rackHelper service
    beforeEach(inject(function (_LogicTopologyHelper_, _serviceTopologyConfig_) {
      // The injector unwraps the underscores (_) from around the parameter names when matching
      Service = _LogicTopologyHelper_;
      Config = _serviceTopologyConfig_;

      // result
      let totalElWidth = Config.elWidths.reduce((el, val) => val + el, 0);
      let remainingSpace = svgWidth - totalElWidth - (Config.widthMargin * 2);
      let step = remainingSpace / (Config.elWidths.length - 1);
      x0 = Config.widthMargin;
      x1 = x0 + Config.elWidths[0] + step;
      x2 = x1 + Config.elWidths[1] + step;
      x3 = x2 + Config.elWidths[2] + step;
      x4 = x3 + Config.elWidths[3] + step;
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
      let [el0x, el1x, el2x, el3x, el4x] = Service.computeElementPosition(svgWidth);
      expect(el0x).toBeSimilar(svgWidth - (x0 + (Config.elWidths[0] / 2)));
      expect(el1x).toBeSimilar(svgWidth - (x1 + (Config.elWidths[1] / 2)));
      expect(el2x).toBeSimilar(svgWidth - (x2 + (Config.elWidths[2] / 2)));
      expect(el3x).toBeSimilar(svgWidth - (x3 + (Config.elWidths[3] / 2)));
      expect(el4x).toBeSimilar(svgWidth - (x4 + (Config.elWidths[4] / 2)));
    });
  });

})();
