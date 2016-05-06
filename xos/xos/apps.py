from suit.apps import DjangoSuitConfig


class MyDjangoSuitConfig(DjangoSuitConfig):
    admin_name = 'XOS'
    menu_position = 'vertical'
    menu_open_first_child = False
    menu = (
      {'label': 'Deployments', 'icon': 'icon-deployment', 'url': '/admin/core/deployment/'},
      {'label': 'Sites', 'icon': 'icon-site', 'url': '/admin/core/site/'},
      {'label': 'Slices', 'icon': 'icon-slice', 'url': '/admin/core/slice/'},
      {'label': 'Users', 'icon': 'icon-user', 'url': '/admin/core/user/'},
      {'label': 'Services', 'icon': 'icon-cog', 'url': '/serviceGrid/'},
    )
