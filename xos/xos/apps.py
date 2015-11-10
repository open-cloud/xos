from suit.apps import DjangoSuitConfig

class MyDjangoSuitConfig(DjangoSuitConfig):
    admin_name = 'XOS'
    menu_position = 'vertical'
    menu_open_first_child = False