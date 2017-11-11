import shutil
import os.path

import pros.common.utils as util
from pros.config.config import Config

class DepotConfig(Config):
    def __init__(self,
                 file=None, name=None, provider=None, location=None,
                 provider_options=None,
                 types=None,
                 root_dir=None):
        self.name = name
        self.provider = provider
        self.location = location
        self.types = list(types)
        self.provider_options = provider_options if provider_options is not None else dict()
        if not file:
            root_dir = root_dir if root_dir is not None else util.get_app_dir()
            file = os.path.join(root_dir, name, 'depot.pros')
        super(DepotConfig, self).__init__(file)
        self.migrate({'registrar': 'provider', 'registrar_options': 'provider_options'})

    def delete(self):
        super(DepotConfig, self).delete()
        shutil.rmtree(self.directory)
