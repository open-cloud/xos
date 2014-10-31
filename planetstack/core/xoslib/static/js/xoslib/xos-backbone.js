if (! window.XOSLIB_LOADED ) {
    window.XOSLIB_LOADED=true;

    SLIVER_API = "/plstackapi/slivers/";
    SLICE_API = "/plstackapi/slices/";
    SLICEDEPLOYMENT_API = "/plstackapi/slice_deployments/";
    SLICEPRIVILEGE_API = "/plstackapi/slice_privileges/";
    SLICEROLE_API = "/plstackapi/slice_roles/";
    NODE_API = "/plstackapi/nodes/";
    SITE_API = "/plstackapi/sites/";
    USER_API = "/plstackapi/users/";
    USERDEPLOYMENT_API = "/plstackapi/user_deployments/";
    DEPLOYMENT_API = "/plstackapi/deployments/";
    IMAGE_API = "/plstackapi/images/";
    NETWORKTEMPLATE_API = "/plstackapi/networktemplates/";
    NETWORKDEPLOYMENT_API = "/plstackapi/networkdeployments/";
    NETWORK_API = "/plstackapi/networks/";
    NETWORKSLIVER_API = "/plstackapi/networkslivers/";
    SERVICE_API = "/plstackapi/services/";

    SLICEPLUS_API = "/xoslib/slicesplus/";

    XOSModel = Backbone.Model.extend({
        /* from backbone-tastypie.js */
        //idAttribute: 'resource_uri',

        /* from backbone-tastypie.js */
        url: function() {
                    var url = this.attributes.resource_uri;

                    if (!url) {
                        url = this.urlRoot + this.id;
                    }

                    if (!url) {
                        // XXX I'm not sure this does anything useful
                        url = ( _.isFunction( this.collection.url ) ? this.collection.url() : this.collection.url );
                        url = url || this.urlRoot;
                    }

                    // remove any existing query parameters
                    url && ( url.indexOf("?") > -1 ) && ( url = url.split("?")[0] );

                    url && ( url += ( url.length > 0 && url.charAt( url.length - 1 ) === '/' ) ? '' : '/' );

                    url && ( url += "?no_hyperlinks=1" );

                    return url;
            },

            listMethods: function() {
                var res = [];
                for(var m in this) {
                    if(typeof this[m] == "function") {
                        res.push(m)
                    }
                }
                return res;
            }
    });

    XOSCollection = Backbone.Collection.extend({
        objects: function() {
                    return this.models.map(function(element) { return element.attributes; });
                 },

        initialize: function(){
          this.sortVar = 'name';
          this.sortOrder = 'asc';
        },

        relatedCollections: [],
        foreignCollections: [],

        simpleComparator: function( model ){
          parts=this.sortVar.split(".");
          result = model.get(parts[0]);
          for (index=1; index<parts.length; ++index) {
              result=result[parts[index]];
          }
          return result;
        },

        comparator: function (left, right) {
            var l = this.simpleComparator(left);
            var r = this.simpleComparator(right);

            if (l === void 0) return -1;
            if (r === void 0) return 1;

            if (this.sortOrder=="desc") {
                return l < r ? 1 : l > r ? -1 : 0;
            } else {
                return l < r ? -1 : l > r ? 1 : 0;
            }
        },

        startPolling: function() {
            if (!this._polling) {
                var collection=this;
                setInterval(function() { collection.fetch(); }, 10000);
                this._polling=true;
                this.fetch();
            }
        },

        maybeFetch: function(options){
                // Helper function to fetch only if this collection has not been fetched before.
            if(this._fetched){
                    // If this has already been fetched, call the success, if it exists
                options.success && options.success();
                console.log("alreadyFetched");
                return;
            }

                // when the original success function completes mark this collection as fetched
            var self = this,
            successWrapper = function(success){
                return function(){
                    self._fetched = true;
                    success && success.apply(this, arguments);
                };
            };
            options.success = successWrapper(options.success);
            console.log("call fetch");
            this.fetch(options);
        },

        getOrFetch: function(id, options){
                // Helper function to use this collection as a cache for models on the server
            var model = this.get(id);

            if(model){
                options.success && options.success(model);
                return;
            }

            model = new this.model({
                resource_uri: id
            });

            model.fetch(options);
        },

        filterBy: function(fieldName, value) {
             filtered = this.filter(function(obj) {
                 return obj.get(fieldName) == value;
                 });
             return new this.constructor(filtered);
        },

        /* from backbone-tastypie.js */
        url: function( models ) {
                    var url = this.urlRoot || ( models && models.length && models[0].urlRoot );
                    url && ( url += ( url.length > 0 && url.charAt( url.length - 1 ) === '/' ) ? '' : '/' );

                    // Build a url to retrieve a set of models. This assume the last part of each model's idAttribute
                    // (set to 'resource_uri') contains the model's id.
                    if ( models && models.length ) {
                            var ids = _.map( models, function( model ) {
                                            var parts = _.compact( model.id.split('/') );
                                            return parts[ parts.length - 1 ];
                                    });
                            url += 'set/' + ids.join(';') + '/';
                    }

                    url && ( url += "?no_hyperlinks=1" );

                    return url;
            },

        listMethods: function() {
                var res = [];
                for(var m in this) {
                    if(typeof this[m] == "function") {
                        res.push(m)
                    }
                }
                return res;
            },
    });

    function xoslib() {
        // basic REST
        this.sliver = XOSModel.extend({ urlRoot: SLIVER_API });
        this.sliverCollection = XOSCollection.extend({ urlRoot: SLIVER_API,
                                                       relatedCollections: {"networkSlivers": "sliver"},
                                                       foreignCollections: ["slices", "deployments", "images", "nodes", "users"],
                                                       model: this.sliver});
        this.slivers = new this.sliverCollection();

        this.slice = XOSModel.extend({ urlRoot: SLICE_API });
        this.sliceCollection = XOSCollection.extend({ urlRoot: SLICE_API,
                                                       relatedCollections: {"slivers": "slice", "sliceDeployments": "slice", "slicePrivileges": "slice"},
                                                       foreignCollections: ["services", "sites"],
                                                       model: this.slice});
        this.slices = new this.sliceCollection();

        this.sliceDeployment = XOSModel.extend({ urlRoot: SLICEDEPLOYMENT_API });
        this.sliceDeploymentCollection = XOSCollection.extend({ urlRoot: SLICEDEPLOYMENT_API,
                                                       foreignCollections: ["slices", "deployments"],
                                                       model: this.slice});
        this.sliceDeployments = new this.sliceDeploymentCollection();

        this.slicePrivilege = XOSModel.extend({ urlRoot: SLICEPRIVILEGE_API });
        this.slicePrivilegeCollection = XOSCollection.extend({ urlRoot: SLICEPRIVILEGE_API,
                                                       foreignCollections: ["slices", "users", "sliceRoles"],
                                                       model: this.slice});
        this.slicePrivileges = new this.slicePrivilegeCollection();

        this.sliceRole = XOSModel.extend({ urlRoot: SLICEROLE_API });
        this.sliceRoleCollection = XOSCollection.extend({ urlRoot: SLICEROLE_API,
                                                       model: this.slice});
        this.sliceRoles = new this.sliceRoleCollection();

        this.node = XOSModel.extend({ urlRoot: NODE_API });
        this.nodeCollection = XOSCollection.extend({ urlRoot: NODE_API,
                                                       foreignCollections: ["sites", "deployments"],
                                                       model: this.node});
        this.nodes = new this.nodeCollection();

        this.site = XOSModel.extend({ urlRoot: SITE_API });
        this.siteCollection = XOSCollection.extend({ urlRoot: SITE_API,
                                                       model: this.site});
        this.sites = new this.siteCollection();

        this.user = XOSModel.extend({ urlRoot: USER_API });
        this.userCollection = XOSCollection.extend({ urlRoot: USER_API,
                                                       relatedCollections: {"slicePrivileges": "user", "slices": "owner", "userDeployments": "user"},
                                                       foreignCollections: ["sites"],
                                                       model: this.user});
        this.users = new this.userCollection();

        this.userDeployment = XOSModel.extend({ urlRoot: USER_API });
        this.userDeploymentCollection = XOSCollection.extend({ urlRoot: USERDEPLOYMENT_API,
                                                       foreignCollections: ["users","deployments"],
                                                       model: this.user});
        this.userDeployments = new this.userDeploymentCollection();

        this.deployment = XOSModel.extend({ urlRoot: DEPLOYMENT_API });
        this.deploymentCollection = XOSCollection.extend({ urlRoot: DEPLOYMENT_API,
                                                           model: this.deployment});
        this.deployments = new this.deploymentCollection();

        this.image = XOSModel.extend({ urlRoot: IMAGE_API });
        this.imageCollection = XOSCollection.extend({ urlRoot: IMAGE_API,
                                                           model: this.image});
        this.images = new this.imageCollection();

        this.networkTemplate = XOSModel.extend({ urlRoot: NETWORKTEMPLATE_API });
        this.networkTemplateCollection = XOSCollection.extend({ urlRoot: NETWORKTEMPLATE_API,
                                                           model: this.networkTemplate});
        this.networkTemplates = new this.networkTemplateCollection();

        this.network = XOSModel.extend({ urlRoot: NETWORK_API });
        this.networkCollection = XOSCollection.extend({ urlRoot: NETWORK_API,
                                                           relatedCollections: {"networkDeployments": "network", "networkSlivers": "network"},
                                                           foreignCollections: ["slices", "networkTemplates"],
                                                           model: this.network});
        this.networks = new this.networkCollection();

        this.networkSliver = XOSModel.extend({ urlRoot: NETWORKSLIVER_API });
        this.networkSliverCollection = XOSCollection.extend({ urlRoot: NETWORKSLIVER_API,
                                                           model: this.networkSliver});
        this.networkSlivers = new this.networkSliverCollection();

        this.networkDeployment = XOSModel.extend({ urlRoot: NETWORKDEPLOYMENT_API });
        this.networkDeploymentCollection = XOSCollection.extend({ urlRoot: NETWORKDEPLOYMENT_API,
                                                           model: this.networkDeployment});
        this.networkDeployments = new this.networkDeploymentCollection();

        this.service = XOSModel.extend({ urlRoot: SERVICE_API });
        this.serviceCollection = XOSCollection.extend({ urlRoot: SERVICE_API,
                                                       model: this.service});
        this.services = new this.serviceCollection();

        // enhanced REST
        this.slicePlus = XOSModel.extend({ urlRoot: SLICEPLUS_API, relatedCollections: {'slivers': "slice"} });
        this.slicePlusCollection = XOSCollection.extend({ urlRoot: SLICEPLUS_API,
                                                          model: this.slicePlus});
        this.slicesPlus = new this.slicePlusCollection();

        this.listObjects = function() { return ["slivers", "slices", "nodes", "sites", "users", "deployments"]; };
    };

    xos = new xoslib();

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    (function() {
      var _sync = Backbone.sync;
      Backbone.sync = function(method, model, options){
        options.beforeSend = function(xhr){
          var token = getCookie("csrftoken");
          xhr.setRequestHeader('X-CSRFToken', token);
        };
        return _sync(method, model, options);
      };
    })();
}
