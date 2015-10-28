'use strict';

describe('The Xos Backbone', () => {

  beforeEach(() => {
    $.extend(xosdefaults,{
      test: {config: true}
    });
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

  describe('The define_model method', () => {

    var testLib;

    beforeEach(() => {
      var TestLibDefinition = function(){
        /* eslint-disable no-invalid-this*/
        this.allCollectionNames = [];
        this.allCollections = [];
        /* eslint-enable no-invalid-this*/
      };

      testLib = new TestLibDefinition();
    });

    it('should create a model and attach it to xos lib', () => {
      define_model(testLib, {
        urlRoot: 'testUrl',
        modelName: 'testModel'
      });

      expect(testLib.allCollectionNames[0]).toEqual('testModels');
      expect(typeof testLib['testModel']).toBe('function');

    });

    describe('when a model is created', () => {
      var model;
      beforeEach(() => {
        define_model(testLib, {
          urlRoot: 'testUrl',
          modelName: 'testModel',
          // collectionName: 'testCollection',
          relatedCollections: {instances: 'slices'},
          foreignCollections: ['sites'],
          foreignFields: {slice: 'slices'},
          m2mFields: {sites: 'sites'},
          listFields: ['name'],
          detailFields: ['name', 'age'],
          addFields: ['add'],
          inputType: {add: 'checkbox'}
        });
        /*eslint-disable new-cap*/
        model = new testLib.testModel();
        /*eslint-enable new-cap*/

        // add defaults and validator for `testModel`
        xosdefaults['testModel'] = {name: 'Scott'};
        xosvalidators['testModel'] = {network_ports: ['portspec']};
      });

      it('should have a name', () => {
        expect(model.modelName).toEqual('testModel');
      });

      it('should have a default collectionName', () => {
        expect(model.collectionName).toEqual('testModels');
      });

      describe('whith a custom collectionName', () => {
        var customCollectionName;
        beforeEach(() => {
          define_model(testLib, {
            urlRoot: 'collUrl',
            modelName: 'customCollectionName',
            collectionName: 'myCollection'
          });

          /*eslint-disable new-cap*/
          customCollectionName = new testLib.customCollectionName();
          /*eslint-enable new-cap*/
        });

        it('should have the custom collectionName', () => {
          expect(customCollectionName.collectionName).toBe('myCollection');
        });

        afterEach(() => {
          customCollectionName = null;
        });
      });

      it('should have a valid url', () => {
        expect(model.url()).toEqual('testUrl/?no_hyperlinks=1');
      });

      it('should have related collections', () => {
        expect(model.relatedCollections).toEqual({instances: 'slices'});
      });

      it('should have foreign collections', () => {
        expect(model.foreignCollections).toEqual(['sites']);
      });

      it('should have foreign fields', () => {
        expect(model.foreignFields).toEqual({slice: 'slices'});
      });

      it('should have m2m fields', () => {
        expect(model.m2mFields).toEqual({sites: 'sites'});
      });

      it('should have list field', () => {
        expect(model.listFields).toEqual(['name']);
      });

      it('should have deatil field', () => {
        expect(model.detailFields).toEqual(['name', 'age']);
      });

      it('should have add field', () => {
        expect(model.addFields).toEqual(['add']);
      });

      it('should have input types defined', () => {
        expect(model.inputType).toEqual({add: 'checkbox'});
      });

      it('should have standard defaults', () => {
        expect(model.defaults).toEqual({name: 'Scott'});
      });

      describe('when default are defined', () => {

        var extendDefault;
        beforeEach(() => {
          define_model(testLib, {
            urlRoot: 'collUrl',
            modelName: 'extendDefault',
            defaults: extend_defaults('testModel', {surname: 'Baker'})
          });

          /*eslint-disable new-cap*/
          extendDefault = new testLib.extendDefault();
          /*eslint-enable new-cap*/
        });

        it('should return new defaults', () => {
          expect(extendDefault.defaults).toEqual({name: 'Scott', surname: 'Baker'});
        });

        afterEach(() => {
          extendDefault = null;
        });
      });

      it('should add default validators', () => {
        expect(model.validators).toEqual({network_ports: ['portspec']});
      });

      describe('when validators are defined', () => {

        var extendValidators;
        beforeEach(() => {
          define_model(testLib, {
            urlRoot: 'collUrl',
            modelName: 'testModel',
            validators: {site: ['notBlank']}
          });

          /*eslint-disable new-cap*/
          extendValidators = new testLib.testModel();
          /*eslint-enable new-cap*/
        });

        it('should return extended validators', () => {
          expect(extendValidators.validators).toEqual({network_ports: ['portspec'], site: ['notBlank']});
        });

        afterEach(() => {
          extendValidators = null;
        });
      });

      it('should have the default xosValidate method', () => {
        expect(typeof model.xosValidate).toEqual('function');
      });

      describe('when xosValidate is defined', () => {

        var extendXosValidate;
        beforeEach(() => {
          define_model(testLib, {
            urlRoot: 'collUrl',
            modelName: 'testModel',
            xosValidate: {site: ['notBlank']}
          });

          /*eslint-disable new-cap*/
          extendXosValidate = new testLib.testModel();
          /*eslint-enable new-cap*/
        });

        // NOTE if I can override with an object a also can override with functions
        // testing with the object is mush simpler

        it('should be overwritten', () => {
          expect(extendXosValidate.xosValidate).toEqual({site: ['notBlank']});
        });

        afterEach(() => {
          extendXosValidate = null;
        });
      });

      // TBT
      // - xosValidate
      // - Test the default
      // - Test override

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