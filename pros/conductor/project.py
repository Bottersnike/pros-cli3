from pros.config.config import Config, ConfigNotFoundException
import os.path


class Project(Config):
    def __init__(self, path: str='.', create: bool=False, raise_on_error: bool=True, defaults: dict=None):
        file = Project.find_project(path or '.')
        if file is None and create:
            file = os.path.join(path, 'project.pros')
        elif file is None and raise_on_error:
            raise ConfigNotFoundException('A project config was not found for {}'.format(path))

        if defaults is None:
            defaults = {}
        self.kernel: str = defaults.get('kernel', None)  # kernel version
        self.target: str = defaults.get('target', 'cortex').lower()  # VEX Hardware target (V5/Cortex)
        self.libraries = defaults.get('libraries', {})
        self.output = defaults.get('output', 'bin/output.bin')
        self.upload_options = defaults.get('upload_options', {})
        self.project_name: str = defaults.get('project_name', None)
        super(Project, self).__init__(file, error_on_decode=raise_on_error)

    @property
    def location(self):
        return os.path.dirname(self.save_file)

    @property
    def name(self):
        return self.project_name or os.path.basename(self.location) or os.path.basename(self.output) or 'pros'

    @staticmethod
    def find_project(path):
        path = os.path.abspath(path)
        if os.path.isfile(path):
            return path
        elif os.path.isdir(path):
            for n in range(10):
                if path is not None and os.path.isdir(path):
                    files = [f for f in os.listdir(path)
                             if os.path.isfile(os.path.join(path, f)) and f.lower() == 'project.pros']
                    if len(files) == 1:  # found a project.pros file!
                        return os.path.join(path, files[0])
                    path = os.path.dirname(path)
                else:
                    return None
        return None
