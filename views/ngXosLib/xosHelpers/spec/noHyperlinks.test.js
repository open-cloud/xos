/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  describe('The xos.helper module', function(){
    describe('The NoHyperlinks factory', () => {

      let httpProviderObj, noHyperlinks;

      beforeEach(() => {
        module(
          'xos.helpers',
          ($httpProvider) => {
            //save our interceptor
            httpProviderObj = $httpProvider;
          }
        );

        inject(function (_NoHyperlinks_) {
          noHyperlinks = _NoHyperlinks_
        });

        httpProviderObj.interceptors.push('NoHyperlinks');

      });

      it('should set NoHyperlinks interceptor', () => {
        expect(httpProviderObj.interceptors).toContain('NoHyperlinks');
      });

      it('should attach ?no_hyperlinks=1 to the request url', () => {
        let result = noHyperlinks.request({url: 'sample.url'});
        expect(result.url).toEqual('sample.url?no_hyperlinks=1');
      });

      it('should NOT attach ?no_hyperlinks=1 to the request url if is HTML', () => {
        let result = noHyperlinks.request({url: 'sample.html'});
        expect(result.url).toEqual('sample.html');
      });

    });
  });
})();

