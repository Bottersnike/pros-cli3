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
        return (self._manifest is None) or (datetime.now() - self._last_check > cli_config().update_frequency)

    def get_manifest(self, force: bool = False) -> UpgradeManifestV1:
        if not force and not self.has_stale_manifest:
            return self._manifest

        pros.common.logger(__name__).info('Fetching upgrade manifest...')
        import requests
        import jsonpickle
        import json

        channel_url = f'https://www.cs.purdue.edu/~berman5/{self.release_channel.value}'
        for manifest in manifests:
            resp = requests.get(f'{channel_url}/{manifest.__name__}.json')
            if resp.status_code == 200:
                try:
                    self._manifest = jsonpickle.decode(resp.text, keys=True)
                    pros.common.logger(__name__).debug(self._manifest)
                    self._last_check = datetime.now()
                    self.save()
                    break
                except json.decoder.JSONDecodeError as e:
                    pros.common.logger(__name__).debug(e)
        return self._manifest

    @property
    def needs_upgrade(self) -> bool:
        manifest = self.get_manifest()
        if manifest is None:
            return False
        return manifest.needs_upgrade

    def describe_update(self) -> str:
        manifest = self.get_manifest()
        assert manifest is not None
        return manifest.describe_update()

    @property
    def can_perform_upgrade(self):
        manifest = self.get_manifest()
        assert manifest is not None
        return manifest.can_perform_upgrade

    def perform_upgrade(self) -> bool:
        manifest = self.get_manifest()
        assert manifest is not None
        return manifest.perform_upgrade()

    def describe_post_upgrade(self) -> str:
        manifest = self.get_manifest()
        assert manifest is not None
        return manifest.describe_post_install()
