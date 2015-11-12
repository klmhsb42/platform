from subprocess import check_output
from syncloud_app import logger
from models import AppVersions
import jsonpickle
import psutil

import convertible
from syncloud_platform.config.config import PlatformConfig

SAM_BIN = '/opt/app/sam/bin/sam'


class SamStub:

    def __init__(self):
        self.logger = logger.get_logger('ServerFacade')

    def update(self, release=None):
        args = [SAM_BIN, 'update']
        if release:
            args += ['--release', release]
        return self.__run(args)

    def install(self, app_id):
        return self.__run([SAM_BIN, 'install', app_id])

    def upgrade(self, app_id):
        self.run_detached('{0} upgrade {1}'.format(SAM_BIN, app_id))

    def remove(self, app_id):
        return self.__run([SAM_BIN, 'remove', app_id])

    def list(self):
        result = self.__run([SAM_BIN, 'list'])
        return convertible.to_object(result, convertible.List(item_type=AppVersions))

    def user_apps(self):
        return [a for a in self.list() if not a.app.required]

    def installed_user_apps(self):
        return [a for a in self.user_apps() if a.installed_version]

    def installed_all_apps(self):
        return [a for a in self.list() if a.installed_version]

    def get_app(self, app_id):
        return next(a for a in self.list() if a.app.id == app_id)

    def run_detached(self, command):
        # The only reliable way to detach a command
        ssh_command = "ssh localhost -p {0} -o StrictHostKeyChecking=no 'nohup {1} </dev/null >/dev/null 2>&1 &'".format(
            PlatformConfig().get_ssh_port(), command)
        self.logger.info('ssh command: {0}'.format(ssh_command))
        output = check_output(ssh_command, shell=True)
        self.logger.info(output)

    def __run(self, cmd_args):
        cmd_line = ' '.join(cmd_args)
        output = check_output(cmd_line, shell=True)
        result = jsonpickle.decode(output)
        return result['data']

    def is_running(self):
        for p in psutil.get_process_list():
            for arg in p.cmdline():
                if SAM_BIN in arg:
                    return True
        return False
