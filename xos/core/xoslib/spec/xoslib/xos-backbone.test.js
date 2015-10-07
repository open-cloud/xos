'use strict';

describe('The Xos Backbone', () => {
  describe('get_defaults mehod', () => {

    beforeEach(() => {
      xosdefaults = {
        test: {config: true}
      };
    });

    it('should return default config', () => {
      let res = get_defaults('test');
      expect(res).toEqual({config: true});
    });

    it('should return undefined', () => {
      let res = get_defaults('notset');
      expect(res).toBeUndefined();
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
      expect(res).toEqual('onlab.us/?no_hyperlinks=1')
    });

    it('should remove query params', () => {
      const ctx = {attributes: {resource_uri: 'onlab.us?query=params'}};
      let res = model.url.apply(ctx);
      expect(res).toEqual('onlab.us/?no_hyperlinks=1')
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
    }

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