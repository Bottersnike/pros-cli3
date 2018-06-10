import sys
from enum import Enum
from typing import *

import pros.common.ui as ui
from .upgrade_manifest_v1 import UpgradeManifestV1


class PlatformsV2(Enum):
    Unknown = 0
    Windows86 = 1
    Windows64 = 2
    MacOS = 3
    Linux = 4
    Pip = 5


class ActionV2(Enum):
    Nothing = 0,
    OpenExplorer = 1,
    OpenShell = 2,
    Browser = 3


class DownloadDescriptionV2(NamedTuple):
    url: str
    instructions: str
    action: 'ActionV2'


class UpgradeManifestV2(UpgradeManifestV1):
    """
    an Upgrade Manifest capable of determining if there is an update, and possibly an installer to download,
    but without the knowledge of how to run the installer
    """

    def __init__(self):
        super().__init__()
        self.download_urls: Dict['PlatformsV2', 'DownloadDescriptionV2'] = {}

        self._platform: 'PlatformsV2' = None

        self._last_file: Optional[str] = None

    @property
    def platform(self) -> 'PlatformsV2':
        """
        Attempts to detect the current platform type
        :return: The detected platform type, or Unknown
        """
        if self._platform is not None:
            return self._platform
        if getattr(sys, 'frozen', False):
            import BUILD_CONSTANTS
            frozen_platform = getattr(BUILD_CONSTANTS, 'FROZEN_PLATFORM_V1', None)
            if isinstance(frozen_platform, str):
                if frozen_platform.startswith('Windows86'):
                    self._platform = PlatformsV2.Windows86
                elif frozen_platform.startswith('Windows64'):
                    self._platform = PlatformsV2.Windows64
                elif frozen_platform.startswith('MacOS'):
                    self._platform = PlatformsV2.MacOS
        else:
            try:
                from pip._vendor import pkg_resources
                results = [p for p in pkg_resources.working_set if p.project_name.startswith('pros-cli')]
                if any(results):
                    self._platform = PlatformsV2.Pip
            except ImportError:
                pass
        if not self._platform:
            self._platform = PlatformsV2.Unknown
        return self._platform

    @property
    def can_perform_upgrade(self) -> bool:
        return self.platform in self.download_urls.keys()

    def perform_upgrade(self) -> bool:
        assert self.can_perform_upgrade

        manifest = self.download_urls[self.platform]
        if manifest.action == ActionV2.Nothing:
            return True
        if manifest.action == ActionV2.Browser:
            from click import launch
            return launch(manifest.url) == 0

        self._last_file = None
        from pros.common.utils import download_file
        self._last_file = download_file(manifest.url)

        if manifest.action == ActionV2.OpenExplorer:
            from click import launch
            return launch(f, locate=True) == 0
        if manifest.action == ActionV2.OpenShell and \
                not (hasattr(sys.stdin, 'isatty') and sys.stdin.isatty()):
            # TODO
            pass
        ui.echo(f'File downloaded to {self._last_file}')
        self.describe_post_install(self._last_file)
        return True

    def describe_post_install(self, downloaded_file: str=None, **kwargs) -> str:
        assert self.can_perform_upgrade
        return self.download_urls[self.platform].instructions.replace('//FILE\\\\', downloaded_file or self._last_file or '<downloaded_file>')

    def __repr__(self):
        return repr({
            'platform': self.platform,
            **self.__dict__
        })
