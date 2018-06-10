import pros.common.ui as ui
from pros.cli.common import *
from pros.config.cli_config import cli_config


@click.group(cls=PROSGroup)
def misc_commands_cli():
    pass


@misc_commands_cli.command()
@click.option('--force-check', default=False, is_flag=True,
              help='Force check for updates, disregarding auto-check frequency')
@click.option('--no-install', default=False, is_flag=True,
              help='Only check if a new version is available, do not attempt to install')
@default_options
def upgrade(force_check, no_install):
    from pros.upgrade import UpgradeManager
    manager = UpgradeManager()
    manifest = manager.get_manifest(force_check)
    if manifest is None:
        ui.logger(__name__).error('Failed to get upgrade information. Try running with --debug for more information')
        return -1
    if no_install:
        ui.finalize('upgradeInfo', manifest)
    else:
        ui.echo(manifest.describe_update())
        manifest.perform_upgrade()
        ui.finalize('upgradeComplete', manifest.describe_post_install())


if os.path.exists(os.path.join(__file__, '..', '..', '..', '.git')):
    @misc_commands_cli.command()
    @click.option('--version', default=None)
    @click.option('--download-url', prompt=True)
    @click.option('--info-url', prompt=True)
    def create_upgrade_manifest(version, download_url, info_url):
        from pros.upgrade.manifests.upgrade_manifest_v1 import UpgradeManifestV1
        from semantic_version import Version
        import jsonpickle
        if version is None:
            version = get_version()
        upgrade_manifest = UpgradeManifestV1()
        upgrade_manifest.version = Version(version)
        upgrade_manifest.download_url = download_url
        upgrade_manifest.info_url = info_url
        print(jsonpickle.encode(upgrade_manifest))
