'use strict';

describe('The ResponseHandler service', () => {
  
  var ResponseHandler, done;

  beforeEach(module('xos.UITutorial'));
  beforeEach(module('templates'));

  beforeEach(inject(function (_ResponseHandler_) {
    // The injector unwraps the underscores (_) from around the parameter names when matching
    ResponseHandler = _ResponseHandler_;
    done = jasmine.createSpy('done');
  }));

  describe('the parse method', () => {
    it('should return an html template for a collection', () => {
      const collection = [
        {id: 1, deleted: true, name: 'one'},
        {id: 2, deleted: true, name: 'two'}
      ];

      const collectionHtml = `
      <div>
        <p>Corresponding js code: <code>jsCode</code></p>
        <div class="json"><div class="jsonCollection">[<div class="jsonObject">{"id":1,"name":"one"},</code></div><div class="jsonObject">{"id":2,"name":"two"}</code></div>]</div></div>
      </div>
    `;
      ResponseHandler.parse(collection, 'jsCode', done);
      expect(done).toHaveBeenCalledWith(collectionHtml)
    });

    it('should return an html template for an object', () => {
      const object = {id: 1, deleted: true, name: 'one'};

      const objectHtml = `
      <div>
        <p>Corresponding js code: <code></code></p>
        <div class="json"><div class="jsonObject">{"id":1,"name":"one"}</code></div></div>
      </div>
    `;
      ResponseHandler.parse(object, '', done);
      expect(done).toHaveBeenCalledWith(objectHtml)
    });
  });
});