/* eslint-disable */
(function(){

window.InstanceView = Backbone.View.extend({
    tagName: 'li',
    className: 'instance',

    events: {
        'click .permalink': 'navigate'
    },

    initialize: function(){
        this.model.bind('change', this.render, this);
    },

    navigate: function(e){
        this.trigger('navigate', this.model);
        e.preventDefault();
    },

    render: function(){
        $(this.el).html(ich.instanceTemplate(this.model.toJSON()));
        return this;
    }
});


window.DetailApp = Backbone.View.extend({
    events: {
        'click .home': 'home'
    },

    home: function(e){
        this.trigger('home');
        e.preventDefault();
    },

    render: function(){
        $(this.el).html(ich.detailApp(this.model.toJSON()));
        return this;
    }
});

window.ListView = Backbone.View.extend({
    initialize: function(){
        _.bindAll(this, 'addOne', 'addAll');

        this.collection.bind('add', this.addOne);
        this.collection.bind('reset', this.addAll, this);
        this.views = [];
    },

    addAll: function(){
        this.views = [];
        this.collection.each(this.addOne);
    },

    addOne: function(instance){
        var view = new InstanceView({
            model: instance
        });
        $(this.el).prepend(view.render().el);
        this.views.push(view);
        view.bind('all', this.rethrow, this);
    },

    rethrow: function(){
        this.trigger.apply(this, arguments);
    }

});

window.ListApp = Backbone.View.extend({
    el: "#app",

    rethrow: function(){
        this.trigger.apply(this, arguments);
    },

    render: function(){
        console.log("listApp.render");
        console.log(this.collection);
        $(this.el).html(ich.listApp({}));
        var list = new ListView({
            collection: this.collection,
            el: this.$('#instances')
        });
        list.addAll();
        list.bind('all', this.rethrow, this);
    }
});


window.Router = Backbone.Router.extend({
    routes: {
        '': 'list',
        ':id/': 'detail'
    },

    navigate_to: function(model){
        var path = (model && model.get('id') + '/') || '';
        console.log("Router.navigate_to");
        this.navigate(path, true);
    },

    detail: function(){ console.log("Router.detail"); },

    list: function(){ console.log("Router.list"); }
});

$(function(){
    window.app = window.app || {};
    app.router = new Router();
    app.instances = xos.instances; //new XOSLib.instances();
    app.list = new ListApp({
        el: $("#app"),
        collection: app.instances
    });
    app.detail = new DetailApp({
        el: $("#app")
    });
    app.router.bind('route:list', function(){
        app.instances.maybeFetch({
            success: _.bind(app.list.render, app.list)
        });
    });
    app.router.bind('route:detail', function(id){
        app.instances.getOrFetch(app.instances.urlRoot + id + '/', {
            success: function(model){
                app.detail.model = model;
                app.detail.render();
            }
        });
    });

    app.instances.maybeFetch({
        success: _.bind(app.list.render, app.list)
    });

    app.list.bind('navigate', app.router.navigate_to, app.router);
    app.detail.bind('home', app.router.navigate_to, app.router);
    Backbone.history.start({
        pushState: true,
        silent: app.loaded
    });
});
})();
/* eslint-enable */
