'use strict';

describe('The XOSModel', () => {

  var model;

  beforeEach(() => {
    model = new XOSModel();
  });

  describe('url method', () => {
    it('should set the correct url', () => {
      const ctx = {attributes: {resource_uri: 'onlab.us'}};
      let res = model.url.apply(ctx);
      expect(res).toEqual('onlab.us/?no_hyperlinks=1')
    });

    it('should remove query params', () => {
      const ctx = {attributes: {resource_uri: 'onlab.us?query=params'}};
      let res = model.url.apply(ctx);
      expect(res).toEqual('onlab.us/?no_hyperlinks=1')
    });
  });

  describe('listMethods method', () => {
    it('should list all methods in instance', () => {
      const instance = {
        m1: () => {},
        m2: () => {}
      };

      let res = model.listMethods.apply(instance);
      expect(res.length).toBe(2);
      expect(res[0]).toEqual('m1');
    });
  });
});