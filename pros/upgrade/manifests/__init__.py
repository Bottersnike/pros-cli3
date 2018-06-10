from .upgrade_manifest_v1 import UpgradeManifestV1
from .upgrade_manifest_v2 import UpgradeManifestV2, PlatformsV2, DownloadDescriptionV2, ActionV2

from typing import *

# Order of files
manifests = [UpgradeManifestV2, UpgradeManifestV1]  # type: List[Type]
__all__ = ['UpgradeManifestV1', 'UpgradeManifestV2', 'manifests', 'PlatformsV2', 'DownloadDescriptionV2', 'ActionV2']
