import os

from pros.conductor.templates.template_identifier import TemplateIdentifier
from .depot_config import DepotConfig

class Depot(object):
    def __init__(self, arg):
        if isinstance(arg, DepotConfig):
            self.config = arg
        elif isinstance(arg, str):
            if os.path.exists(arg):
                if arg.endswith('depot.pros'):
                    self.config = DepotConfig(file=arg)
                elif os.path.isdir(arg) and os.path.exists(os.path.join(arg, 'depot.pros')):
                    self.config = DepotConfig(file=os.path.join(arg, 'depot.pros'))
                else:
                    raise ValueError("Couldn't deduce meaning of {}".format(arg))
            elif arg.index(os.path.sep) < 0:
                self.config = DepotConfig(name=arg)
            else:
                raise ValueError("Couldn't deduce meaning of {}".format(arg))
        elif isinstance(arg, TemplateIdentifier) and arg.depot is not None:
            self.config = DepotConfig(name=arg.depot)
        else:
            raise ValueError("Couldn't deduce meaning of {}".format(arg))

    def get_online_templates(self):
        pass

    def get_offline_templates(self):
        pass

    def get_all_templates(self):
        return [self.get_online_templates(), self.get_offline_templates()]

    @classmethod
    def install_template(cls, template):
        template.install()

    @classmethod
    def uninstall_template(cls, template):
        template.uninstall()

    @classmethod
    def upgrade_template(cls, template):
        template.upgrade()

    @classmethod
    def delete_template(cls, template):
        template.delete()
