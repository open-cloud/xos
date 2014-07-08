SLIVER_API = "/plstackapi/slivers/";

XOSCollection = Backbone.Collection.extend({
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

        model = new Sliver({
            resource_uri: id
        });

        model.fetch(options);
    }
});

function xoslib() {
    this.sliver = Backbone.Model.extend({ urlRoot: SLIVER_API });
    this.slivers = XOSCollection.extend({ urlRoot: SLIVER_API,
                                    model: this.sliver});
};

XOSLib = new xoslib();
