import sys

import requests.certs
from cx_Freeze import Executable, setup

try:  # for pip >= 10 -- https://stackoverflow.com/a/49867265/3175586
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
import pros

install_reqs = [str(r.req) for r in parse_requirements('requirements.txt', session=False)]

build_exe_options = {
    'packages': ['ssl', 'requests', 'idna'],
    "include_files": [(requests.certs.where(), 'cacert.pem')],
    'excludes': ['pip', 'distutils'],  # optimization excludes
    'constants': ['CLI_VERSION=\'{}\''.format(open('version').read().strip())],
    'include_msvcr': True
    # 'zip_include_packages': [],
    # 'zip_exclude_packages': []
}

build_mac_options = {
    'bundle_name': 'PROS CLI',
    'iconfile': 'pros.icns'
}

modules = []
for pkg in [pros]:
    modules.append(pkg.__name__)

if sys.platform == 'win32':
    extension = '.exe'
else:
    extension = ''

setup(
    name='pros-cli-v5',
    version=open('pip_version').read().strip(),
    packages=modules,
    url='https://github.com/purduesigbots/pros-cli',
    license='MPL-2.0',
    author='Purdue ACM Sigbots',
    author_email='pros_development@cs.purdue.edu',
    description='Command Line Interface for managing PROS projects',
    options={"build_exe": build_exe_options, 'bdist_mac': build_mac_options},
    install_requires=install_reqs,
    executables=[Executable('pros/cli/main.py', targetName=f'prosv5{extension}'),
                 Executable('pros/cli/compile_commands/intercept-cc.py', targetName=f'intercept-cc{extension}'),
                 Executable('pros/cli/compile_commands/intercept-cc.py', targetName=f'intercept-c++{extension}')]
)

if sys.argv[1] == 'build_exe':
    import distutils.util

    build_dir = './build/exe.{}-{}.{}'.format(distutils.util.get_platform(), sys.version_info[0], sys.version_info[1])
    import shutil
    import platform

    shutil.make_archive('pros_cli-{}-{}-{}'.format(open('version').read().strip(), platform.system()[0:3].lower(),
                                                   platform.architecture()[0]), 'zip', build_dir, '.')
