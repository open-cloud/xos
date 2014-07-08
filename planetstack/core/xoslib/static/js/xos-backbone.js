SLIVER_API = "/plstackapi/slivers/";
SLICE_API = "/plstackapi/slices/";

XOSModel = Backbone.Model.extend({
    /* from backbone-tastypie.js */
    idAttribute: 'resource_uri',

    /* from backbone-tastypie.js */
    url: function() {
		// Use the id if possible
		var url = this.id;

		// If there's no idAttribute, try to have the collection construct a url. Fallback to 'urlRoot'.
		if ( !url ) {
			url = this.collection && ( _.isFunction( this.collection.url ) ? this.collection.url() : this.collection.url );
                        console.log(url);
			url = url || this.urlRoot;
		}

		url && ( url += ( url.length > 0 && url.charAt( url.length - 1 ) === '/' ) ? '' : '/' );

                url && ( url += "?no_hyperlinks=1" );

		return url;
	},
});

XOSCollection = Backbone.Collection.extend({
    objects: function() {
                return this.models.map(function(element) { return element.attributes; });
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
});

function xoslib() {
    this.sliver = XOSModel.extend({ urlRoot: SLIVER_API });
    this.sliverCollection = XOSCollection.extend({ urlRoot: SLIVER_API,
                                                   model: this.sliver});
    this.slivers = new this.sliverCollection();

    this.slice = XOSModel.extend({ urlRoot: SLICE_API });
    this.sliceCollection = XOSCollection.extend({ urlRoot: SLICE_API,
                                                   model: this.slice});
    this.slices = new this.sliceCollection();
};

xos = new xoslib();
