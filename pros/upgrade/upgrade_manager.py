import os.path
from datetime import datetime
from enum import Enum
from typing import *

import pros.common
from pros.config import Config
from pros.config.cli_config import cli_config
from .manifests import *


class ReleaseChannel(Enum):
    Stable = 'stable'
    Beta = 'beta'


class UpgradeManager(Config):
    def __init__(self, file=None):
        if file is None:
            file = os.path.join(cli_config().directory, 'upgrade.pros.json')
        self._last_check: datetime = datetime.min
        self._manifest: Optional[UpgradeManifestV1] = None
        self.release_channel: ReleaseChannel = ReleaseChannel.Stable

        super().__init__(file)

    @property
    def has_stale_manifest(self):
        return self._manifest is None or datetime.now() - self._last_check > cli_config().update_frequency

    def get_manifest(self, force: bool = False) -> UpgradeManifestV1:
        if not force and not self.has_stale_manifest:
            return self._manifest

        pros.common.logger(__name__).info('Fetching upgrade manifest...')
        import requests
        import jsonpickle
        import json

        channel_url = f'https://purduesigbots.github.io/pros-mainline/{self.release_channel}'
        for manifest in manifests:
            resp = requests.get(f'{channel_url}/{manifest.__name__}.json')
            if resp.status_code == 200:
                try:
                    self._manifest = jsonpickle.decode(resp.text)
                    self._last_check = datetime.now()
                    break
                except json.decoder.JSONDecodeError:
                    pass
