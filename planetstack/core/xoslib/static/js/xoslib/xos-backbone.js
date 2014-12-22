if (! window.XOSLIB_LOADED ) {
    window.XOSLIB_LOADED=true;

    SLIVER_API = "/plstackapi/slivers/";
    SLICE_API = "/plstackapi/slices/";
    SLICEROLE_API = "/plstackapi/slice_roles/";
    NODE_API = "/plstackapi/nodes/";
    SITE_API = "/plstackapi/sites/";
    USER_API = "/plstackapi/users/";
    USERDEPLOYMENT_API = "/plstackapi/user_deployments/";
    DEPLOYMENT_API = "/plstackapi/deployments/";
    IMAGE_API = "/plstackapi/images/";
    IMAGEDEPLOYMENTS_API = "/plstackapi/imagedeployments/";
    NETWORKTEMPLATE_API = "/plstackapi/networktemplates/";
    NETWORK_API = "/plstackapi/networks/";
    NETWORKSLIVER_API = "/plstackapi/networkslivers/";
    SERVICE_API = "/plstackapi/services/";
    SLICEPRIVILEGE_API = "/plstackapi/slice_privileges/";
    NETWORKDEPLOYMENT_API = "/plstackapi/networkdeployments/";
    FLAVOR_API = "/plstackapi/flavors/";

    /* changed as a side effect of the big rename
    SLICEDEPLOYMENT_API = "/plstackapi/slice_deployments/";
    USERDEPLOYMENT_API = "/plstackapi/user_deployments/";
    */

    SLICEDEPLOYMENT_API = "/plstackapi/slicedeployments/";
    USERDEPLOYMENT_API = "/plstackapi/userdeployments/";

    SLICEPLUS_API = "/xoslib/slicesplus/";

    XOSModel = Backbone.Model.extend({
        /* from backbone-tastypie.js */
        //idAttribute: 'resource_uri',

        /* from backbone-tastypie.js */
        url: function() {
                    var url = this.attributes.resource_uri;

                    if (!url) {
                        if (this.id) {
                            url = this.urlRoot + this.id;
                        } else {
                            // this happens when creating a new model.
                            url = this.urlRoot;
                        }
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
            },

            save: function(attributes, options) {
                if (this.preSave) {
                    this.preSave();
                }
                return Backbone.Model.prototype.save.call(this, attributes, options);
            },

            getChoices: function(fieldName, excludeChosen) {
                choices=[];
                if (fieldName in this.m2mFields) {
                    for (index in xos[this.m2mFields[fieldName]].models) {
                        candidate = xos[this.m2mFields[fieldName]].models[index];
                        if (excludeChosen && idInArray(candidate.id, this.attributes[fieldName])) {
                            continue;
                        }
                        choices.push(candidate.id);
                    }
                }
                return choices;
            },

            /* If a 'validate' method is supplied, then it will be called
               automatically on save. Unfortunately, save calls neither the
               'error' nor the 'success' callback if the validator fails.

               For now, we're calling our validator 'xosValidate' so this
               autoamtic validation doesn't occur.
            */

            xosValidate: function(attrs, options) {
                errors = {};
                foundErrors = false;
                _.each(this.validators, function(validatorList, fieldName) {
                    _.each(validatorList, function(validator) {
                        if (fieldName in attrs) {
                            validatorResult = validateField(validator, attrs[fieldName], this)
                            if (validatorResult != true) {
                                errors[fieldName] = validatorResult;
                                foundErrors = true;
                            }
                        }
                    });
                });
                if (foundErrors) {
                    return errors;
                }
                // backbone.js semantics -- on successful validate, return nothing
            },

            /* uncommenting this would make validate() call xosValidate()
            validate: function(attrs, options) {
                r = this.xosValidate(attrs, options);
                console.log("validate");
                console.log(r);
                return r;
            }, */
    });

    XOSCollection = Backbone.Collection.extend({
        objects: function() {
                    return this.models.map(function(element) { return element.attributes; });
                 },

        initialize: function(){
          this.isLoaded = false;
          this.failedLoad = false;
          this.startedLoad = false;
          this.sortVar = 'name';
          this.sortOrder = 'asc';
          this.on( "sort", this.sorted );
        },

        relatedCollections: [],
        foreignCollections: [],

        sorted: function() {
            //console.log("sorted " + this.modelName);
        },

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

        fetchSuccess: function(collection, response, options) {
            //console.log("fetch succeeded " + collection.modelName);
            this.failedLoad = false;
            this.fetching = false;
            if (!this.isLoaded) {
                this.isLoaded = true;
                Backbone.trigger("xoslib:collectionLoadChange", this);
            }
            this.trigger("fetchStateChange");
            if (options["orig_success"]) {
                options["orig_success"](collection, response, options);
            }
        },

        fetchFailure: function(collection, response, options) {
            //console.log("fetch failed " + collection.modelName);
            this.fetching = false;
            if ((!this.isLoaded) && (!this.failedLoad)) {
                this.failedLoad=true;
                Backbone.trigger("xoslib:collectionLoadChange", this);
            }
            this.trigger("fetchStateChange");
            if (options["orig_failure"]) {
                options["orig_failure"](collection, response, options);
            }
        },

        fetch: function(options) {
            var self=this;
            this.fetching=true;
            //console.log("fetch " + this.modelName);
            if (!this.startedLoad) {
                this.startedLoad=true;
                Backbone.trigger("xoslib:collectionLoadChange", this);
            }
            this.trigger("fetchStateChange");
            if (options == undefined) {
                options = {};
            }
            options["orig_success"] = options["success"];
            options["orig_failure"] = options["failure"];
            options["success"] = function(collection, response, options) { self.fetchSuccess.call(self, collection, response, options); };
            options["failure"] = this.fetchFailure;
            Backbone.Collection.prototype.fetch.call(this, options);
        },

        startPolling: function() {
            if (!this._polling) {
                var collection=this;
                setInterval(function() { collection.fetch(); }, 10000);
                this._polling=true;
                this.fetch();
            }
        },

        refresh: function(refreshRelated) {
            if (!this.fetching) {
                this.fetch();
            }
            if (refreshRelated) {
                for (related in this.relatedCollections) {
                    related = xos[related];
                    if (!related.fetching) {
                        related.fetch();
                    }
                }
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

        /* filterBy: note that this yields a new collection. If you pass that
              collection to a CompositeView, then the CompositeView won't get
              any events that trigger on the original collection.

              Using this function is probably wrong, and I wrote
              FilteredCompositeView() to replace it.
        */

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

    function define_model(lib, attrs) {
        modelName = attrs.modelName;
        modelClassName = modelName;
        collectionClassName = modelName + "Collection";

        if (!attrs.addFields) {
            attrs.addFields = attrs.detailFields;
        }

        attrs.inputType = attrs.inputType || {};
        attrs.foreignFields = attrs.foreignFields || {};
        attrs.m2mFields = attrs.m2mFields || {};
        attrs.readOnlyFields = attrs.readOnlyFields || [];
        attrs.detailLinkFields = attrs.detailLinkFields || ["id","name"];

        if (!attrs.collectionName) {
            attrs.collectionName = modelName + "s";
        }
        collectionName = attrs.collectionName;

        modelAttrs = {}
        collectionAttrs = {}

        for (key in attrs) {
            value = attrs[key];
            if ($.inArray(key, ["urlRoot", "modelName", "collectionName", "listFields", "addFields", "detailFields", "detailLinkFields", "foreignFields", "inputType", "relatedCollections", "foreignCollections"])>=0) {
                modelAttrs[key] = value;
                collectionAttrs[key] = value;
            }
            if ($.inArray(key, ["validate", "preSave", "readOnlyFields"])) {
                modelAttrs[key] = value;
            }
        }

        if ((typeof xosdefaults !== "undefined") && xosdefaults[modelName]) {
            modelAttrs["defaults"] = xosdefaults[modelName];
        }

        if ((typeof xosvalidators !== "undefined") && xosvalidators[modelName]) {
            modelAttrs["validators"] = xosvalidators[modelName];
        }

        lib[modelName] = XOSModel.extend(modelAttrs);

        collectionAttrs["model"] = lib[modelName];

        lib[collectionClassName] = XOSCollection.extend(collectionAttrs);
        lib[collectionName] = new lib[collectionClassName]();

        lib.allCollectionNames.push(collectionName);
        lib.allCollections.push(lib[collectionName]);
    };

    function xoslib() {
        this.allCollectionNames = [];
        this.allCollections = [];

        /* Give an id, the name of a collection, and the name of a field for models
           within that collection, lookup the id and return the value of the field.
        */

        this.idToName = function(id, collectionName, fieldName) {
            linkedObject = xos[collectionName].get(id);
            if (linkedObject == undefined) {
                return "#" + id;
            } else {
                return linkedObject.attributes[fieldName];
            }
        };

        define_model(this, {urlRoot: SLIVER_API,
                            relatedCollections: {"networkSlivers": "sliver"},
                            foreignCollections: ["slices", "deployments", "images", "nodes", "users", "flavors"],
                            foreignFields: {"creator": "users", "image": "images", "node": "nodes", "deploymentNetwork": "deployments", "slice": "slices", "flavor": "flavors"},
                            modelName: "sliver",
                            listFields: ["backend_status", "id", "name", "instance_id", "instance_name", "slice", "deploymentNetwork", "image", "node", "flavor"],
                            addFields: ["slice", "deploymentNetwork", "flavor", "image", "node"],
                            detailFields: ["backend_status", "name", "instance_id", "instance_name", "slice", "deploymentNetwork", "flavor", "image", "node", "creator"],
                            preSave: function() { if (!this.attributes.name && this.attributes.slice) { this.attributes.name = xos.idToName(this.attributes.slice, "slices", "name"); } },
                            });

        define_model(this, {urlRoot: SLICE_API,
                           relatedCollections: {"slivers": "slice", "slicePrivileges": "slice", "networks": "owner"},
                           foreignCollections: ["services", "sites"],
                           foreignFields: {"service": "services", "site": "sites"},
                           listFields: ["backend_status", "id", "name", "enabled", "description", "slice_url", "site", "max_slivers", "service"],
                           detailFields: ["backend_status", "name", "site", "enabled", "description", "slice_url", "max_slivers"],
                           inputType: {"enabled": "checkbox"},
                           modelName: "slice",
                           xosValidate: function(attrs, options) {
                               errors = XOSModel.prototype.xosValidate(this, attrs, options);
                               // validate that slice.name starts with site.login_base
                               site = attrs.site || this.site;
                               if ((site!=undefined) && (attrs.name!=undefined)) {
                                   site = xos.sites.get(site);
                                   if (attrs.name.indexOf(site.attributes.login_base+"_") != 0) {
                                        errors = errors || {};
                                        errors["name"] = "must start with " + site.attributes.login_base + "_";
                                   }
                               }
                               return errors;
                             },
                           });

        define_model(this, {urlRoot: SLICEPRIVILEGE_API,
                            foreignCollections: ["slices", "users", "sliceRoles"],
                            modelName: "slicePrivilege",
                            foreignFields: {"user": "users", "slice": "slices", "role": "sliceRoles"},
                            listFields: ["backend_status", "id", "user", "slice", "role"],
                            detailFields: ["backend_status", "user", "slice", "role"],
                            });

        define_model(this, {urlRoot: SLICEROLE_API,
                            modelName: "sliceRole",
                            listFields: ["backend_status", "id", "role"],
                            detailFields: ["backend_status", "role"],
                            });

        define_model(this, {urlRoot: NODE_API,
                            foreignCollections: ["sites", "deployments"],
                            modelName: "node",
                            foreignFields: {"site": "sites", "deployment": "deployments"},
                            listFields: ["backend_status", "id", "name", "site", "deployment"],
                            detailFields: ["backend_status", "name", "site", "deployment"],
                            });

        define_model(this, {urlRoot: SITE_API,
                            relatedCollections: {"users": "site", "slices": "site", "nodes": "site"},
                            modelName: "site",
                            listFields: ["backend_status", "id", "name", "site_url", "enabled", "login_base", "is_public", "abbreviated_name"],
                            detailFields: ["backend_status", "name", "abbreviated_name", "url", "enabled", "is_public", "login_base"],
                            inputType: {"enabled": "checkbox", "is_public": "checkbox"},
                            });

        define_model(this, {urlRoot: USER_API,
                            relatedCollections: {"slicePrivileges": "user", "slices": "owner"},
                            foreignCollections: ["sites"],
                            modelName: "user",
                            foreignFields: {"site": "sites"},
                            listFields: ["backend_status", "id", "username", "firstname", "lastname", "phone", "user_url", "site"],
                            detailFields: ["backend_status", "username", "firstname", "lastname", "phone", "user_url", "site"],
                            });

        define_model(this, { urlRoot: DEPLOYMENT_API,
                             relatedCollections: {"nodes": "deployment", "slivers": "deploymentNetwork"},
                             m2mFields: {"flavors": "flavors", "sites": "sites", "images": "images"},
                             modelName: "deployment",
                             listFields: ["backend_status", "id", "name", "backend_type", "admin_tenant"],
                             detailFields: ["backend_status", "name", "backend_type", "admin_tenant", "flavors", "sites", "images"],
                             inputType: {"flavors": "picker", "sites": "picker", "images": "picker"},
                             });

        define_model(this, {urlRoot: IMAGE_API,
                            model: this.image,
                            modelName: "image",
                            listFields: ["backend_status", "id", "name", "disk_format", "container_format", "path"],
                            detailFields: ["backend_status", "name", "disk_format", "admin_tenant"],
                            });

        define_model(this, {urlRoot: NETWORKTEMPLATE_API,
                            modelName: "networkTemplate",
                            listFields: ["backend_status", "id", "name", "visibility", "translation", "sharedNetworkName", "sharedNetworkId"],
                            detailFields: ["backend_status", "name", "description", "visibility", "translation", "sharedNetworkName", "sharedNetworkId"],
                            });

        define_model(this, {urlRoot: NETWORK_API,
                            relatedCollections: {"networkSlivers": "network"},
                            foreignCollections: ["slices", "networkTemplates"],
                            modelName: "network",
                            foreignFields: {"template": "networkTemplates", "owner": "slices"},
                            listFields: ["backend_status", "id", "name", "template", "ports", "labels", "owner"],
                            detailFields: ["backend_status", "name", "template", "ports", "labels", "owner"],
                            });

        define_model(this, {urlRoot: NETWORKSLIVER_API,
                            modelName: "networkSliver",
                            foreignFields: {"network": "networks", "sliver": "slivers"},
                            listFields: ["backend_status", "id", "network", "sliver", "ip", "port_id"],
                            detailFields: ["backend_status", "network", "sliver", "ip", "port_id"],
                            });

        define_model(this, {urlRoot: SERVICE_API,
                            modelName: "service",
                            listFields: ["backend_status", "id", "name", "enabled", "versionNumber", "published"],
                            detailFields: ["backend_status", "name", "description", "versionNumber"],
                            });

        define_model(this, {urlRoot: FLAVOR_API,
                            modelName: "flavor",
                            m2mFields: {"deployments": "deployments"},
                            listFields: ["backend_status", "id", "name", "flavor", "order", "default"],
                            detailFields: ["backend_status", "name", "description", "flavor", "order", "default", "deployments"],
                            inputType: {"default": "checkbox", "deployments": "picker"},
                            });

        /* DELETED in site-controller branch

        define_model(this, {urlRoot: NETWORKDEPLOYMENT_API,
                            modelName: "networkDeployment",
                            foreignFields: {"network": "networks", "deployment": "deployments"},
                            listFields: ["backend_status", "id", "network", "deployment", "net_id"],
                            detailFields: ["backend_status", "network", "deployment", "net_id"],
                            });

        define_model(this, {urlRoot: SLICEDEPLOYMENT_API,
                           foreignCollections: ["slices", "deployments"],
                           modelName: "sliceDeployment",
                           foreignFields: {"slice": "slices", "deployment": "deployments"},
                           listFields: ["backend_status", "id", "slice", "deployment", "tenant_id"],
                           detailFields: ["backend_status", "slice", "deployment", "tenant_id"],
                           });

        define_model(this, {urlRoot: USERDEPLOYMENT_API,
                            foreignCollections: ["users","deployments"],
                            modelName: "userDeployment",
                            foreignFields: {"deployment": "deployments", "user": "users"},
                            listFields: ["backend_status", "id", "user", "deployment", "kuser_id"],
                            detailFields: ["backend_status", "user", "deployment", "kuser_id"],
                            });

        END stuff deleted in site-controller branch */

        /* not deleted, but seems obsolete and should be replaced by ManyToMany

        define_model(this, {urlRoot: IMAGEDEPLOYMENTS_API,
                            modelName: "imageDeployment",
                            foreignCollections: ["images", "deployments"],
                            listFields: ["backend_status", "id", "image", "deployment", "glance_image_id"],
                            detailFields: ["backend_status", "image", "deployment", "glance_image_id"],
                            });

        */

        // enhanced REST
        // XXX this really needs to somehow be combined with Slice, to avoid duplication
        define_model(this, {urlRoot: SLICEPLUS_API,
                            relatedCollections: {'slivers': "slice"},
                            modelName: "slicePlus",
                            collectionName: "slicesPlus"});

        this.listObjects = function() { return this.allCollectionNames; };

        this.getCollectionStatus = function() {
            stats = {isLoaded: 0, failedLoad: 0, startedLoad: 0};
            for (index in this.allCollections) {
                collection = this.allCollections[index];
                if (collection.isLoaded) {
                    stats["isLoaded"] = stats["isLoaded"] + 1;
                }
                if (collection.failedLoad) {
                    stats["failedLoad"] = stats["failedLoad"] + 1;
                }
                if (collection.startedLoad) {
                    stats["startedLoad"] = stats["startedLoad"] + 1;
                }
            }
            stats["completedLoad"] = stats["failedLoad"] + stats["isLoaded"];
            return stats;
        };
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
