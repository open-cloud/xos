(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('TemplateHandler', function(_){
    
    this.error = _.template(`<span class="error">[ERROR] <%= msg %></span>`);

    this.instructions = _.template(`
      <div>
        <strong><%= title %></strong>
        <% _.forEach(messages, function(m) { %><p><%= m %></p><% }); %>
      </div>
    `);

    this.resourcesResponse = _.template(`
      <div>
        <p>Corresponding js code: <code><%= jsCode %></code></p>
        <div class="json"><%= res %></div>
      </div>
    `);

    this.jsonObject = _.template(`<div class="jsonObject"><%= JSON.stringify(obj) %><%=comma%></code></div>`);

    this.jsonCollection = _.template(`<div class="jsonCollection">[<% _.forEach(collection, function(item) { %><%= item %><%}); %>]</div>`);
  });
})();