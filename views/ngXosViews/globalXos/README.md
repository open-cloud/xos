# Global XOS View

To onboard this view, use:
```
# You can use this recipe to load the dashboard in the system:
GlobalXos:
  type: tosca.nodes.DashboardView
  properties:
    url: template:xosGlobalXos

# And this recipe to activate the dashboard for a user:
padmin@vicci.org:
  type: tosca.nodes.User
  properties:
    no-create: true
    no-delete: true
  requirements:
    - globalXos_dashboard:
        node: GlobalXos
        relationship: tosca.relationships.UsesDashboard
```