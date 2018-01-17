import json.decoder
import os

import jsonpickle

import pros.common


class ConfigNotFoundException(Exception):
    def __init__(self, message, *args, **kwargs):
        super(ConfigNotFoundException, self).__init__(args, kwargs)
        self.message = message


class Config(object):
    """
    A configuration object that's capable of being saved as a JSON object
    """

    def __init__(self, file, error_on_decode=False):
        pros.common.logger(__name__).debug('Opening {} ({})'.format(file, self.__class__.__name__))
        self.save_file = file
        # __ignored property has any fields which shouldn't be included the pickled config file
        self.__ignored = self.__dict__.get('_Config__ignored', [])
        self.__ignored.append('save_file')
        self.__ignored.append('_Config__ignored')
        if file:
            # If the file already exists, update this new config with the values in the file
            if os.path.isfile(file):
                with open(file, 'r') as f:
                    try:
                        result = jsonpickle.decode(f.read())
                        if isinstance(result, dict):
                            if 'py/state' in result:
                                class_name = '{}.{}'.format(self.__class__.__module__, self.__class__.__qualname__)
                                pros.common.logger(__name__).debug(
                                    'Coercing {} to {}'.format(result['py/object'], class_name))
                                self.__dict__.update(result['py/state'])
                            else:
                                self.__dict__.update(result)
                        elif isinstance(result, object):
                            self.__dict__.update(result.__dict__)
                    except (json.decoder.JSONDecodeError, AttributeError) as e:
                        if error_on_decode:
                            pros.common.logger(__name__).exception(e)
                            raise e
                        else:
                            pros.common.logger(__name__).debug(e)
                            pass
            # obvious
            elif os.path.isdir(file):
                raise ValueError('{} must be a file, not a directory'.format(file))
            # The file didn't exist when we created, so we'll save the default values
            else:
                try:
                    self.save()
                except Exception as e:
                    if error_on_decode:
                        pros.common.logger(__name__).exception(e)
                        raise e
                    else:
                        pros.common.logger(__name__).debug('Failed to save {} ({})'.format(file, e))

    def __getstate__(self):
        state = self.__dict__.copy()
        if '_Config__ignored' in self.__dict__:
            for key in [k for k in self.__ignored if k in state]:
                del state[key]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def delete(self):
        if os.path.isfile(self.save_file):
            os.remove(self.save_file)

    def save(self, file: str = None) -> None:
        if file is None:
            file = self.save_file
        if pros.common.isdebug(__name__):
            pros.common.logger(__name__).debug('Pretty formatting {} file'.format(self.__class__.__name__))
            jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
        else:
            jsonpickle.set_encoder_options('json')
        if os.path.dirname(file):
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            f.write(jsonpickle.encode(self))
            pros.common.logger(__name__).debug('Saved {}'.format(file))

    def migrate(self, migration):
        for (old, new) in migration.iteritems():
            if self.__dict__.get(old) is not None:
                self.__dict__[new] = self.__dict__[old]
                del self.__dict__[old]

    @property
    def directory(self) -> str:
        return os.path.dirname(os.path.abspath(self.save_file))
