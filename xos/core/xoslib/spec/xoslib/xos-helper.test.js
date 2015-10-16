'use strict';

describe('The Xos Helper', () => {
  var f;
  beforeEach(() => {
    f = jasmine.getFixtures();
    f.fixturesPath = 'base/spec/xoslib/fixtures/xos-utils';
  });

  describe('XOSDetailView', () => {

    describe('onFormDataInvalid', () => {

      // TODO capire come applicare le funzioni di xosHelper su un template adHoc

      const err = {name: "must start with mysite_"};
      var view;
      beforeEach(() => {
        console.log('ciao');
        f.set(`
          <script tpye="text/template" id="fake-template">
            <div>
              <input name="name" />
            </div>
          </script>
        `);
        console.log('zio');

        view = XOSDetailView.extend({
          template: '#fake-template'
        });
        console.log('************' + view);
      });

      it('should show an error', () => {

        console.log(view);

        view.onFormDataInvalid(err);


        expect($('.alert').length).toBe(1);
      });
    });

  });

});