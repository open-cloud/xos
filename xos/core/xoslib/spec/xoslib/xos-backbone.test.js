'use strict';

describe('The Xos Backbone', () => {

  beforeEach(() => {
    xosdefaults = {
      test: {config: true}
    };
  });

  describe('get_defaults mehod', () => {

    it('should return default config', () => {
      let res = get_defaults('test');
      expect(res).toEqual({config: true});
    });

    it('should return undefined', () => {
      let res = get_defaults('notset');
      expect(res).toBeUndefined();
    });

  });

  describe('The extend_defaults method', () => {

    it('should return an extended config', () => {
      let extended = extend_defaults('test', {extended: true});
      expect(extended).toEqual({config: true, extended: true});
    });

    it('should return an new config', () => {
      let extended = extend_defaults('notset', {extended: true});
      expect(extended).toEqual({extended: true});
    });

  });

  describe('getCookie method with no cookie', () => {

    beforeEach(() => {
      document.cookie = 'fakeCookie=true=;expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    });

    it('should return null', () => {
      let res = getCookie('fakeCookie');
      expect(res).toBeNull();
    });
  });

  describe('getCookie method with a fake cookie', () => {

    beforeEach(() => {
      document.cookie = 'fakeCookie=true';
    });

    it('should return a cookie value', () => {
      let res = getCookie('fakeCookie');
      expect(res).toEqual('true');
    });
  });
});

describe('The XOSModel', () => {

  var model;

  beforeEach(() => {
    model = new XOSModel();
  });

  describe('url method', () => {
    it('should set the correct url', () => {
      const ctx = {attributes: {resource_uri: 'onlab.us'}};
      let res = model.url.apply(ctx);
      expect(res).toEqual('onlab.us/?no_hyperlinks=1');
    });

    it('should remove query params', () => {
      const ctx = {attributes: {resource_uri: 'onlab.us?query=params'}};
      let res = model.url.apply(ctx);
      expect(res).toEqual('onlab.us/?no_hyperlinks=1');
    });
  });

  describe('listMethods method', () => {

    const instance = {
      m1: () => {},
      m2: () => {}
    };

    it('should list all methods in instance', () => {
      let res = model.listMethods.apply(instance);
      expect(res.length).toBe(2);
      expect(res[0]).toEqual('m1');
    });
  });

  describe('the Save method', () => {
    const ctxPS = {
      preSave: () => {}
    };

    const args = ['attr', 'opts'];

    beforeEach(() => {
      spyOn(ctxPS, 'preSave');
      spyOn(Backbone.Model.prototype, 'save');
    });

    it('should call the preSave method', () => {
      model.save.apply(ctxPS, args);
      expect(ctxPS.preSave).toHaveBeenCalled();
      expect(Backbone.Model.prototype.save).toHaveBeenCalledWith(args[0], args[1]);
    });

    it('should not call the preSave method', () => {
      model.save.apply({}, args);
      expect(ctxPS.preSave).not.toHaveBeenCalled();
      expect(Backbone.Model.prototype.save).toHaveBeenCalledWith(args[0], args[1]);
    });
  });

  describe('the getChoices method', () => {

    const instance = {
      m2mFields: {'flavors': 'flavors', 'sites': 'sites', 'images': 'images'}
    };

    xit('should be tested, what is this doing?', () => {
      model.getChoices.apply(instance);
    });
  });

  describe('the xosValidate method', () => {

    const instance = {
      validators: {'network_ports': ['portspec']}
    };

    const validAttrs = {network_ports: 'tcp 123'};

    it('should call specified validator on a field and pass', () => {
      let err = model.xosValidate.apply(instance, [validAttrs]);
      expect(err).toBeUndefined();
    });

    // set wrong value and recall xosValidate
    const invalidAttrs = {network_ports: 'abd 456'};

    it('should call specified validator on a field and not pass', () => {
      let err = model.xosValidate.apply(instance, [invalidAttrs]);
      expect(err).not.toBeUndefined();
      expect(err).toEqual({network_ports: 'must be a valid portspec (example: \'tcp 123, udp 456-789\')'});
    });
  });
});