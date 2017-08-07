
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


/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 6/22/16.
 */

(function () {
  'use strict';
  describe('The Site Encoder service', () => {
    let service, toscaBase, siteGetPromise, SiteSpy, rootScope;

    const toscaBaseDefault = {
      topology_template: {
        node_templates: {}
      }
    };

    const siteResponse = {
      name: 'MySite'
    };

    const expected = [{
      topology_template: {
        node_templates: {
          'MySite': {
            type: 'tosca.nodes.Site',
          }
        }
      }
    }, siteResponse];

    beforeEach(module('xos.serviceGrid'));
    beforeEach(module('templates'));

    beforeEach(inject((SiteEncoder, Sites, $q, $rootScope) => {
      toscaBase = angular.copy(toscaBaseDefault);
      service = SiteEncoder;
      rootScope = $rootScope;

      siteGetPromise= $q.defer();
      SiteSpy = Sites;
      spyOn(SiteSpy, 'get').and.callFake(function(){
        return {$promise: siteGetPromise.promise};
      });
    }));

    describe('given a Site Id', () => {
      it('should return the correct JSON structure', (done) => {
        service.buildTosca({id: 1}, toscaBase)
          .then(res => {
            expect(res).toEqual(expected);
            done();
          });
        siteGetPromise.resolve(siteResponse);
        rootScope.$apply();
      });
    });
  });
})();

