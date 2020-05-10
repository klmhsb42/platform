from os.path import join

from syncloud_platform.gaplib import gen
from syncloudlib import logger


class Nginx:
    def __init__(self, platform_config, systemctl, device_info):
        self.systemctl = systemctl
        self.config = platform_config
        self.device_info = device_info
        self.log = logger.get_logger('nginx')

    def reload_internal(self):
        self.systemctl.reload_service('platform.nginx-internal')
    
    def reload_public(self):
        self.systemctl.reload_service('platform.nginx-public')

    def init_config(self):
        domain = self.device_info.domain()
        variables = { 'user_domain': domain }
        gen.generate_file_jinja(
            join(self.config.config_dir(), 'nginx', 'public.conf'), 
            join(self.config.nginx_config_dir(), 'nginx.conf'),
            variables)
