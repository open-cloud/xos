(function(){

window.SliverView = Backbone.View.extend({
    tagName: 'li',
    className: 'sliver',

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
        $(this.el).html(ich.sliverTemplate(this.model.toJSON()));
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

    addOne: function(sliver){
        var view = new SliverView({
            model: sliver
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
            el: this.$('#slivers')
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
    app.slivers = xos.slivers; //new XOSLib.slivers();
    app.list = new ListApp({
        el: $("#app"),
        collection: app.slivers
    });
    app.detail = new DetailApp({
        el: $("#app")
    });
    app.router.bind('route:list', function(){
        app.slivers.maybeFetch({
            success: _.bind(app.list.render, app.list)
        });
    });
    app.router.bind('route:detail', function(id){
        app.slivers.getOrFetch(app.slivers.urlRoot + id + '/', {
            success: function(model){
                app.detail.model = model;
                app.detail.render();
            }
        });
    });

    app.slivers.maybeFetch({
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
