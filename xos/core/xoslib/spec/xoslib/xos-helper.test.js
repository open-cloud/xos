/* eslint-disable no-unused-vars*/
'use strict';

describe('The Xos Helper', () => {
  var f;
  beforeEach(() => {
    f = jasmine.getFixtures();
    f.fixturesPath = 'base/spec/xoslib/fixtures/xos-utils';
  });

  describe('XOSDetailView', () => {

    describe('onFormDataInvalid', () => {

      // TODO understand how to attach XOSDetailView to a custom template and test its methods

      const err = {name: 'must start with mysite_'};
      var view;
      beforeEach(() => {
        try{
          f.set(`
            <script type="text/template" id="fake-template">
              <div>
                <input name="name" />
              </div>
            </script>
          `);
        }
        catch(e){
          console.log('err: ' + e);
        }

        view = XOSDetailView.extend({
          template: '#fake-template'
        });

      });

      xit('should show an error', () => {

        // view.onFormDataInvalid(err);
        // view().onFormDataInvalid(err)

        expect($('.alert').length).toBe(1);
      });
    });

  });

});